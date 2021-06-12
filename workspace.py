import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from extendedTk import Fileview
from extendedTk import NumberedTextFrame

from highlight import Highlighter

from pygments.lexers.python import PythonLexer
from pygments.lexers.markup import MarkdownLexer
from pygments.lexers.tcl import TclLexer
from pygments.lexers.c_cpp import CLexer
from pygments.lexers.configs import IniLexer

import os
import pathlib

class WorkspaceTab:
    def __init__(self, master, name, token, style):

        self.frame = NumberedTextFrame(master, style=style, wrap=tk.NONE, bd=0, padx=5, pady=5)
        master.add(self.frame, text=name)
        master.select(self.frame)

        self.path = None
        self.index = master.index(self.frame)

        lexers = {
            '.py': PythonLexer(),
            '.md': MarkdownLexer(),
            '.tcl': TclLexer(),
            '.c': CLexer(),
            '.h': CLexer(),
            '.ini' : IniLexer()
        }
        lexer = lexers.get(pathlib.Path(name).suffix, None)
        self.frame.text.highlighter = Highlighter(self.frame.text, token, lexer)

    def change_path(self, new_path) -> str:
        if not new_path or new_path == self.path:
            return None

        name = os.path.relpath(new_path)
        self.path = new_path
        self.frame.master.tab(self.index, text=name)
        return name

    def read(self, filename) -> bool:
        try:
            self.frame.text.read(filename)
            self.path = filename
        except UnicodeDecodeError as e:
            messagebox.showerror("UnicodeDecodeError", "Could not open {0}: \n{1}".format(filename, e))
            return False
        except FileNotFoundError as e:
            messagebox.showerror("FileNotFoundError", "Could not open {0}: \n{1}".format(filename, e))
            return False
        return True

    def write(self) -> bool:
        try:
            self.frame.text.write(self.path)
        except Exception as e:
            messagebox.showerror("Error", "Could not save {0}: \n{1}".format(self.path, e))
            return False
        return True


class Workspace(ttk.PanedWindow):
    def __init__(self, master, location, token, style=None, **kw):
        super().__init__(master, **kw)

        self.location = location
        self.style = style
        self._token = token

        # content
        self.notebook = ttk.Notebook(self)
        self.tabs = {}

        self.fileview = Fileview(self, style=style, location=location, title="Explorer")

        # adding content to the workspace
        self.add(self.fileview)
        self.add(self.notebook)

        # events
        # TODO: <Configure> event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        self.fileview.tree.bind("<<TreeviewOpen>>", self.on_open)

    def on_open(self, *args):
        filename = self.fileview.focus_path()
        if not os.path.isdir(filename):
            self.load_tab(filename)
    
    def on_tab_changed(self, event):
        # print(self.notebook.index("current"))
        pass

    def get_current_name(self):
        return self.notebook.tab("current", option="text")

    def change_tab_path(self, name, new_path):
        tab = self.tabs.pop(name, None)
        if tab:
            new_name = tab.change_path(new_path)
            self.tabs[new_name] = tab

        return tab

    def delete_tab(self, name=None):
        if name and name in self.tabs:
            tab = self.tabs.pop(name)
            self.notebook.forget(tab.index)
        else:
            self.tabs.pop(self.get_current_name())
            self.notebook.forget("current")

    def load_tab(self, path):
        directory= self.location
        name = os.path.join(directory, path) if path else "untitled"
        if name in self.tabs:   # tab with this name is already open
            self.notebook.select(self.tabs[name].index)
            return 1

        # add to tab dict
        self.tabs[name] = WorkspaceTab(self.notebook, name, self._token, self.style)

        if path and not self.tabs[name].read(name):
            self.delete_tab()
            return -1

        return 0

    def save_tab(self, path=None):
        current = self.get_current_name()
        tab = self.tabs[current]
        name = tab.change_path(path)
        if name:
            self.tabs.pop(current)
            self.tabs[name] = tab

        if tab.path:
            return 0 if tab.write() else -1, tab.path

        # current tab does not have a path yet and no path was specified
        return 1, None
