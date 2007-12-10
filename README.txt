=================================================
"Presentable" GUIs with Styles, Skins, and Layout
=================================================


----------------------------------
Style Sheets, Skins, and Rendering
----------------------------------

>>> from peak.ui import rendering


Renderer Objects
================

Style rules operate on ``Renderer`` objects.  Normally, renderer objects are
created automatically, then passed to your rendering rules.  For demonstration
purposes, however, we'll create a renderer manually::

    >>> skin = rendering.Defaults()
    >>> r = rendering.Renderer(skin, None, 42)


Renderer Attributes
-------------------

Renderers can have a ``parent`` renderer, which is ``None`` for a root
renderer::

    >>> print r.parent
    None

They have a ``subject``, which is the object to be rendered, and an ``output``
which will hold the rendered result::

    >>> r.subject
    42

    >>> print r.output
    None

They know what skin they will use to create their target, along with what
skin will be used to create child components (by default, it's the same one)::

    >>> r.skin is skin
    True

    >>> r.child_skin is skin
    True

They have a ``factory`` attribute (which should be set to a function that will
create the output), which will be called with the ``args`` and ``kw``
attributes.  The default factory takes no arguments or keywords, and produces
no output::

    >>> r.args
    ()

    >>> r.kw
    {}

    >>> print r.factory()
    None


Renderer Handlers
-----------------

Renderers have five "handler lists" for callbacks that will be invoked at
various stages of the rendering process.  As with rules, these handlers can
manipulate the renderer's state (or the output object's state), attach add-ons,
etc., as needed.  The five handler lists are as follows::

    >>> r.before_create     # run before factory(*args, **kw) is called
    []
    >>> r.after_create      # run after output = factory(*args, **kw)
    []
    >>> r.find_children     # callbacks must yield subjects for child rendering
    []
    >>> r.add_child         # invoked for each rendered child
    []
    >>> r.finish            # invoked after all children are rendered
    []

Although these look like normal lists, they are in fact a special kind of list,
with two special features for working with callback.  First, they can be
called with positional arguments, returning a list of the results of calling
each item in the list with those arguments::

    >>> r.finish(1,2,3)
    []
    
    >>> r.finish.append(lambda x: x*2)
    >>> r.finish.append(lambda x: x*3)

    >>> r.finish(1)
    [2, 3]

    >>> r.finish(42)
    [84, 126]

    >>> del r.finish[:]

Second, you don't have to use ``append`` to add elements to these lists, and in
fact you generally *shouldn't* do so.  Instead, use the ``add()`` method, which
avoids inserting duplicates::

    >>> r.finish.add(42)
    >>> r.finish
    [42]

    >>> r.finish.add(42)
    >>> r.finish
    [42]

    >>> del r.finish[:]


The Rendering Process
---------------------

The ``.render()`` method of renderers begins by executing any style rules
defined by its skin for the subject being rendered.  These rules can configure
any handlers or attributes necessary, including setting up the ``factory``,
``args``, and ``kw`` attributes if desired.

Once this is done, the ``before_create`` handlers are invoked, giving them a
chance to do any last-minute configuration prior to invoking the ``factory``.
The ``factory`` is then called with the ``args`` and ``kw``, and the result
is placed in the renderer's ``output`` attribute.

Next, the ``after_create`` handlers are invoked, allowing them to do any
post-initialization configuring of the output.

After that, the child rendering phase begins.  The ``find_children`` handlers
are invoked, and each must return a sequence or iterator that yields subjects
to be rendered.  Each of these subjects will have a child renderer created for
it, and a nested rendering operation will be performed.  Each rendered child
will then be passed to the ``add_child`` handlers.

Finally, the ``finish`` handlers are called.  These can manipulate or replace
the ``output``, if desired.

Let's see how it all goes together::


    >>> class MyStyles(rendering.Defaults):
    ...
    ...     class int_rule(rendering.Rule):
    ...         rendering.for_types(int)
    ...
    ...         def before_create(skin, renderer, subject):
    ...             print "before create", renderer, subject
    ...
    ...         args = ('foo',)
    ...         def factory(arg):
    ...             return arg
    ...
    ...         def after_create(skin, renderer, subject):
    ...             print "after create, output =", renderer.output
    ...
    ...         def find_children(skin, renderer, subject):
    ...             print "finding children"
    ...             if subject==42: yield 27
    ...
    ...         def add_child(skin, renderer, child_renderer):
    ...             print "adding child", child_renderer.subject, "->",
    ...             print child_renderer.output
    ...
    ...         def finish(skin, renderer, subject):
    ...             print "finish", renderer, subject
    ...             renderer.output += 'bar '+str(subject)

    >>> print MyStyles().render(42)
    before create <peak.ui.rendering.Renderer object at ...> 42
    after create, output = foo
    finding children
    before create <peak.ui.rendering.Renderer object at ...> 27
    after create, output = foo
    finding children
    finish <peak.ui.rendering.Renderer object at ...> 27
    adding child 27 -> foobar 27
    finish <peak.ui.rendering.Renderer object at ...> 42
    foobar 42

The ``rendering.Rule`` class lets you define handlers and attributes that will
be added to a renderer when the rule matches a subject.  As you can see, any
attribute named as a handler will be added to the renderer's handlers.  Any
other attributes are simply set directly on the renderer.

The ``rendering.for_types()`` decorator must be used within the Rule class'
body, to specify what types the rule will be applied to.
