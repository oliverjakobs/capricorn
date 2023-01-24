import tkinter as tk

from tkinter import ttk, TclError

class AutoScrollbar(ttk.Scrollbar):
    """ Scrollbar that is only visible when needed. Only works with grid. """
    def __init__(self, master=None, **kw):
        super().__init__(master=master, **kw)

    def set(self, first, last):
        first, last = float(first), float(last)
        if first <= 0 and last >= 1:
            self.grid_remove()
        else:
            self.grid()
        super().set(first, last)

class FadingLabel(ttk.Label):
    """ Label that fades back to an idle text after a given time """
    def __init__(self, master=None, delay=2500, **kw):
        """
        :param delay: delay after which the text return to idle
        """
        super().__init__(master=master, **kw)
        self._idle_text = self["text"]
        self._delay = delay

    def write(self, msg):
        self["text"] = msg
        self.after(self._delay, lambda: self.config(text=self._idle_text))


class ThemedText(tk.Text):
    """ Text widget that can be styled """
    def __init__(self, master=None, style="TText", **kw):

        super().__init__(master=master, **kw)

        self._apply_style(style)

    def _apply_style(self, widget_name):
        style = ttk.Style()

        style_config = style.configure('.')

        config = { k: style_config[k] for k in self.configure().keys() if k in style_config }
        config |= (style.configure(widget_name) or {})

        self.configure(config)


class ExtendedText(ThemedText):
    def __init__(self, master=None, **kw):
        """A text widget that report on internal widget commands"""
        super().__init__(master=master, **kw)

        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._dispatch_tk_proxy)

        self._tk_proxies = {}
        self._register_tk_proxy('mark', self._proxy_mark)
        self._register_tk_proxy('insert', self._proxy_insert)
        self._register_tk_proxy('delete', self._proxy_delete)

    #============================================================================
    # tk functions
    #============================================================================
    def _orig_call(self, command, *args):
        return self.tk.call((self._orig, command) + args)

    def _register_tk_proxy(self, command, function):
        """ register a proxy function for a given operation """
        self._tk_proxies[command] = function
        setattr(self, command, function)

    def _dispatch_tk_proxy(self, command, *args):
        f = self._tk_proxies.get(command)
        try:
            if f: return f(*args)
            return self._orig_call(command, *args)
        except TclError as e:
            #print("ignore error:", command, *args)
            pass

    #============================================================================
    # proxy functions
    #============================================================================
    def _proxy_mark(self, *args):
        self._orig_call('mark', *args)

        self.event_generate("<<insert-moved>>")

    def _proxy_insert(self, index, chars, tags=None):
        self._orig_call('insert', index, chars, tags)

        self.event_generate("<<text-changed>>")
        self.event_generate("<<insert-moved>>")

    def _proxy_delete(self, index1, index2=None):
        # Possible Error: paste can cause deletes where index1 is sel.start but text has no selection
        if index1.startswith("sel.") and not self.tag_ranges("sel"):
            return

        self._orig_call('delete', index1, index2)

        self.event_generate("<<text-changed>>")
        self.event_generate("<<insert-moved>>")

    #============================================================================
    # other functions
    #============================================================================
    def set_tab_size(self, size):
        self['tabs'] = self.tk.call("font", "measure", self['font'], size * ' ')


######################################################################

######################################################################
import os

class ExtendendThemes():
    def __init__(self) -> None:
        self.style = ttk.Style()
        self.old_themes = self.style.theme_names()
        self.added_themes = []

    def load_from_files(self, *files):
        for file in files:
            self.style.tk.call('source', os.path.abspath(file))

        self.added_themes = [t for t in self.style.theme_names() if t not in self.old_themes]

    def load_from_str(self, *strings):
        for s in strings:
            self.style.tk.eval(s)
            
        self.added_themes = [t for t in self.style.theme_names() if t not in self.old_themes]

    #TODO: load from pkgIndex.tcl
    def load_from_index(self, dir, index_name='pkgIndex'):
        ...

    def theme_use(self, name):
        self.style.theme_use(name)