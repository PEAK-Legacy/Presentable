"""Rendering, Style Sheets, and Skins"""
import sys
from new import instancemethod
from peak.util.decorators import classy, decorate_class

__all__ = ['StyleSheet', 'Defaults', 'rule', 'Rule', 'Renderer']


_rule_attr = 'peak.ui.rendering rule target classes'


def rule(target_type):
    """Decorate a method as being a renderer for `target_type` instances

    This decorator is used in the body of stylesheet classes to decorate
    """
    def decorator(func):
        setattr(func, _rule_attr, getattr(func, _rule_attr, ())+ (target_type,))
        return func
    return decorator


class HandlerList(list):
    """A list of handlers"""

    __slots__ = ()

    def __call__(self, *args):
        """Call each of the handlers with `args`, returning list of results"""
        return [handler(*args) for handler in self]

    def add(self, item):
        """Add `item` if not already in the list"""
        if item not in self:
            self.append(item)






class Renderer(object):
    """Widget layout builder"""
    output = None
    args = ()
    def factory(self):
        """This will normally be overridden by an instance attribute"""

    def __init__(self, skin, parent, subject):
        self.skin = self.child_skin = skin
        self.parent = parent
        self.subject = subject
        self.kw = {}
        self.before_create = HandlerList()
        self.after_create = HandlerList()
        self.find_children = HandlerList()
        self.add_child = HandlerList()
        self.finish = HandlerList()

    def render(self): #, subject=None):
        """Render the specified child `subject` and return the result

        If `subject` is None, render this renderer's ``.subject``.
        """
        #if subject is not None:
        #    return self.__class__(self.child_skin, self, subject).render()
        subject = self.subject
        for handler in self.skin[subject.__class__]: handler(self, subject)

        self.before_create(self, subject)
        self.output = self.factory(*self.args, **self.kw)
        self.after_create(self, subject)       
        child_renderers = [
            self.__class__(self.child_skin, self, csub)
            for subs in self.find_children(self, subject) for csub in subs
        ]
        for child_r in child_renderers:
            child_r.render()
            self.add_child(self, child_r)
        self.finish(self, subject)
        return self.output

class StyleSheet(type):
    """Metaclass for style sheets"""

    def __init__(self, name, bases, cdict):
        self.__rules = {}
        self.__all = {}
        self.add_rules(cdict)

    def __getitem__(self, key):
        """Get a sequence of rules for type `key`"""
        try:
            return self.__all[key]

        except KeyError:
            # share rule chains with base sheets if possible
            items = dict.fromkeys(
                [b[key] for b in self.__bases__ if isinstance(b, StyleSheet)
                 and b[key]]
            )

            if len(items)==1:   # no need to merge if just one non-empty chain
                all, = items
                if key in self.__rules and self.__rules[key] not in all:
                    all = (self.__rules[key],) + all

            else:
                all = []
                my_mro = self.__mro__
                for k in key.__mro__:
                    for cls in my_mro:
                        if isinstance(cls, StyleSheet):
                            rules = cls.__rules
                            if k in rules and rules[k] not in all:
                                all.append(rules[k])

                all = tuple(all[::-1])

            self.__all[key] = all
            return all


    def __setitem__(self, key, rule):
        """Set rule for type `key` in this style sheet"""
        if key in self.__rules:
            raise KeyError(
                "Can't set %r[%r]=%r when already set to %r" %
                (self, key, rule, self.__rules[key])
            )
        self.__rules[key] = rule
        self.__erase(key)

    def __erase(self, key):
        # Erase cached values
        if key in self.__all:
            del self.__all[key]
        for cls in self.__subclasses__():
            cls.__erase(key)

    def update(self):
        """Subclass this attribute to add rules to this stylesheet"""
        class update(object):
            def __class__(__self, name, bases, cdict):
                if bases != (__self,):
                    raise TypeError("Mixins must have exactly one base", bases)
                for k, v in self.add_rules(cdict).iteritems():
                    if k not in ('__doc__', '__return__', '__module__'):
                        raise TypeError(
                            "Mixins must not include non-rule attributes"
                        )
        return update()

    update = property(update, doc=update.__doc__)

    def add_rules(self, cdict):
        """Add the rules in `cdict`, returning a dict of non-rule attrs"""
        out = cdict.copy()
        for k, v in cdict.iteritems():
            for t in getattr(v, _rule_attr, ()):
                self[t] = v; out.pop(k,v)
        return out


    def __contains__(self, key):
        # This is mostly here so accidental 'in' doesn't lock up
        for rule in self[key]:
            return True
        return False

    def __iter__(self):
        # This is mostly here so accidental 'iter()' doesn't lock up
        d = {}
        for cls in self.__mro__:
            if isinstance(cls, StyleSheet):
                for key in cls.__rules:
                    if key not in d:
                        d[key] = 1
                        yield key


























class Rule(classy):
    """Base class for rules"""

    def __class_call__(cls, skin, renderer, subject):
        ignore = '__return__', '__module__', '__doc__', _rule_attr
        for k, v in cls.__dict__.iteritems():
            if not isinstance(k,str) or k in ignore:
                continue
            old = getattr(renderer, k, None)
            if isinstance(old, HandlerList):
                if hasattr(v, '__get__'):
                    v = v.__get__(skin)
                old.add(v)
            else:
                setattr(renderer, k, v)

    def __class_init__(cls, name, bases, cdict, supr):
        if 'Rule' in globals():
            if _rule_attr not in cdict:
                raise TypeError("Rule class must declare `for_types`")
            d = {}
            for c in cls.__mro__[::1]:
                if c is not Rule and issubclass(c, Rule):
                    d.update(c.__dict__)
            cdict.update(d)
        supr()(cls, name, bases, cdict, supr)


def for_types(*types):
    """Decorate a method as being a renderer for `target_type` instances

    This decorator is used in the body of rule classes to indic
    """
    d = sys._getframe(1).f_locals
    registered = d.get(_rule_attr, ())
    for t in types:
        if t not in registered:
            registered += (t,)
    d[_rule_attr] = registered



class Defaults(object):
    """The Root Stylesheet

    Subclass this (or other stylesheets) to create more, defining rules in the
    body.
    """
    __metaclass__ = StyleSheet
    sheet = object.__dict__['__class__']

    def __init__(self, **kw):
        cls = self.sheet
        for k, v in kw.iteritems():
            if hasattr(cls, k):
                setattr(self, k, v)
            else:
                raise TypeError(
                    "%s() has no keyword argument %r" % (cls.__name__, k)
                )

    def subskin(self, *bases):
        """Return a "subclass" of this skin

        The returned skin will be an instance of a stylesheet created by mixing
        the supplied `bases` and this skin's stylesheet.  It will also be
        initialized with references to the instance variables of this skin.
        (Note that this means state will be shared between parent and child if
        any of those variables refer to mutable objects.)
        """
        cls = self.sheet
        if bases:
            cls = type(cls)('Subskin', bases+(cls,), {})
        return cls(**self.__dict__)

    def render(self, subject):
        """Render `subject` using this skin"""
        return Renderer(self, None, subject).render()

    def __getitem__(self, key):
        """Get the rules for `key`"""
        return [instancemethod(i,self) for i in self.sheet[key]]

