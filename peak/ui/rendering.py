"""Rendering, Style Sheets, and Skins"""

__all__ = ['StyleSheet', 'Defaults',] # 'rule', 'Renderer'






































class StyleSheet(type):
    """Metaclass for style sheets"""

    def __init__(self, name, bases, cdict):
        self.__rules = {}
        self.__all = {}
        # self.add_rules(cdict)

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


    def __setitem__(self, key, value):
        if key in self.__rules:
            raise KeyError(
                "Can't set %r[%r]=%r when already set to %r" %
                (self, key, value, self.__rules[key])
            )
        self.__rules[key] = value
        self.__erase(key)

    def __erase(self, key):
        # Erase cached values
        if key in self.__all:
            del self.__all[key]
        for cls in self.__subclasses__():
            cls.__erase(key)

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

    # def add_rules(self, cdict):

    # update






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
        cls = self.sheet
        if bases:
            cls = type(cls)('Subskin', bases+(cls,), {})
        return cls(**self.__dict__)

    # render(self, target) -> Renderer(self, None, target)

    # __getitem__(self, cls): return (im(i,self) for i in self.sheet[cls])



























