import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

from lib.extendedTk import DigitEntry
from lib.autocomplete import AutocompleteCombobox

class AboutDialog(tk.Toplevel):
    """Modal about dialog for idle"""
    def __init__(self, parent):
        """Create popup, do not return until tk widget destroyed."""
        super().__init__(parent)
        self.configure(borderwidth=5)
        # place dialog below parent if running htest
        self.geometry(f"+{parent.winfo_rootx()+30}+{parent.winfo_rooty()+30}")

        self.create_widgets()
        self.resizable(height=False, width=False)
        self.title('About')
        self.transient(parent)
        self.grab_set()
        
        self.button_ok.focus_set()
        self.bind('<Return>', self.ok)  # dismiss dialog
        self.bind('<Escape>', self.ok)  # dismiss dialog

        self.protocol("WM_DELETE_WINDOW", self.ok)

        self.deiconify()
        self.wait_window()

    def create_widgets(self):
        bg = "#bbbbbb"
        fg = "#000000"

        # content
        frame_content = tk.Frame(self, borderwidth=1, relief=tk.SOLID, bg=bg)

        header = tk.Label(frame_content, text="Capricorn", fg=fg, bg=bg, font=("Courier New", 24, 'bold'))
        header.grid(row=0, column=0, sticky=tk.W, padx=6, pady=10)

        byline_text = "Distraction free writing app." + (5 * '\n')
        byline = tk.Label(frame_content, text=byline_text, fg=fg, bg=bg)
        byline.grid(row=1, column=0, sticky=tk.W, padx=6, pady=5)
        github = tk.Label(frame_content, text="https://github.com/oliverjakobs/capricorn", fg=fg, bg=bg)
        github.grid(row=2, column=0, sticky=tk.W, padx=6, pady=6)

        separator = ttk.Separator(frame_content, orient=tk.HORIZONTAL)
        separator.grid(row=3, column=0, sticky=tk.EW, padx=5, pady=5)

        # buttons
        frame_buttons = tk.Frame(frame_content, bg=bg)

        self.btn_readme = tk.Button(frame_buttons, text="README", width=8, highlightbackground=bg)
        self.btn_readme.pack(side=tk.LEFT, padx=10, pady=10)
        self.btn_copyright = tk.Button(frame_buttons, text="Copyright", width=8, highlightbackground=bg)
        self.btn_copyright.pack(side=tk.LEFT, padx=10, pady=10)
        self.btn_credits = tk.Button(frame_buttons, text="Credits", width=8, highlightbackground=bg)
        self.btn_credits.pack(side=tk.LEFT, padx=10, pady=10)

        frame_buttons.grid(row=4, column=0, sticky=tk.NSEW)

        # footer
        frame_footer = tk.Frame(self)

        self.button_ok = tk.Button(frame_footer, text="Close", padx=6, command=self.ok)
        self.button_ok.pack(padx=5, pady=5)

        frame_content.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        frame_footer.pack(side=tk.BOTTOM, fill=tk.X)


    def ok(self, event=None):
        "Dismiss help_about dialog."
        self.grab_release()
        self.destroy()



class ConfigDialog(tk.Toplevel):
    """Config dialog. """

    def __init__(self, parent, title, apply):
        """Show the tabbed dialog for user configuration. """
        super().__init__(parent)
        self.withdraw()

        self.apply_cb = apply

        self.title(title or 'Preferences')
        x = parent.winfo_rootx() + 20
        y = parent.winfo_rooty() + 30
        self.geometry(f'+{x}+{y}')
        
        self.create_widgets()
        self.resizable(height=tk.FALSE, width=tk.FALSE)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.grab_set()
        self.wm_deiconify()
        self.wait_window()

    def create_widgets(self):
        # notebook
        self.note = ttk.Notebook(self, padding=(4, 6, 4, 0))
        self.note.enable_traversal()

        self.tabs = {
            'General': GeneralPage(self.note),
            'Colors': ColorPage(self.note)
        }

        for name, tab in self.tabs.items():
            self.note.add(tab, text=name)
        
        self.note.pack(side=tk.TOP, expand=tk.TRUE, fill=tk.BOTH)
        
        # buttons
        frame_btns = ttk.Frame(self)

        ttk.Button(frame_btns, text='Ok', command=self.ok, takefocus=False).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_btns, text='Apply', command=self.apply, takefocus=False).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_btns, text='Cancel', command=self.cancel, takefocus=False).pack(side=tk.LEFT, padx=5)

        frame_btns.pack(side=tk.BOTTOM, pady=6)

    def ok(self):
        """Apply config changes, then dismiss dialog. """
        self.apply()
        self.destroy()

    def apply(self):
        """Apply config changes and leave dialog open. """

        config = {}
        for tab in self.tabs.values():
            config |= tab.get_config()

        self.apply_cb(config)

    def cancel(self):
        """Dismiss config dialog. """
        # changes.clear()
        self.destroy()

    def destroy(self):
        self.grab_release()
        super().destroy()


class ColorPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.config = {
            'fg_main':   tk.StringVar(self, '#e1e4e8'),
            'bg_main':   tk.StringVar(self, '#454545'),
            'bg_status': tk.StringVar(self, '#2f2f2f'),
            'fg_text':   tk.StringVar(self, '#000000'),
            'bg_text':   tk.StringVar(self, '#f1f1f1'),
            'fg_title':  tk.StringVar(self, '#a968c2'),
            'scrollbar': tk.StringVar(self, '#6f6f6f')
        }

        self.create_widgets()

    def create_widgets(self):
        self.columnconfigure(0, weight=1)

        row = 0
        for color, var in self.config.items():
            label_color = ttk.Label(self, text=color)
            entry_color = ttk.Entry(self, width=8, textvariable=var)

            label_color.grid(row=row, column=0, sticky=tk.W, padx=5, pady=4)
            entry_color.grid(row=row, column=1, sticky=tk.E, padx=10, pady=4)

            row += 1

    def get_config(self):
        return {
            'colors': {k: v.get() for k,v in self.config.items()}
        }


class GeneralPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.config = {
            'text_width': tk.IntVar(self, 128)
        }

        self.font_config = {
            'Family': tk.StringVar(self, 'Courier New'),
            'Size': tk.IntVar(self, 10),
            'Title Size': tk.IntVar(self, 24),
            'Separator Size': tk.IntVar(self, 16)
        }

        self.create_widgets()

    def create_widgets(self):
        # workspace
        frame_ws = ttk.LabelFrame(self, borderwidth=2, relief=tk.GROOVE, text="Workspace Preferences")

        frame_ws.columnconfigure(0, weight=1)

        text_width_title = ttk.Label(frame_ws, text='Text Width (in characters)')
        text_width_int = DigitEntry(frame_ws, justify=tk.RIGHT, width=8, textvariable=self.config['text_width'])
        
        text_width_title.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        text_width_int.grid(row=0, column=1, sticky=tk.E, padx=10, pady=5)

        frame_ws.pack(side=tk.TOP, padx=5, pady=5, expand=tk.TRUE, fill=tk.BOTH)

        # fonts
        frame_fonts = ttk.LabelFrame(self, borderwidth=2, relief=tk.GROOVE, text="Font Preferences")

        frame_fonts.columnconfigure(0, weight=1)
        
        # font family
        label_font_family = ttk.Label(frame_fonts, text='Family')
        entry_font_family = AutocompleteCombobox(frame_fonts, textvariable=self.font_config['Family'])

        font_names = sorted(set(tkfont.families(self)))
        entry_font_family.set_completion_list(font_names)

        label_font_family.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        entry_font_family.grid(row=0, column=1, sticky=tk.E, padx=10, pady=5)

        # font sizes
        row = 1
        for name, var in list(self.font_config.items())[1:]:
            label = ttk.Label(frame_fonts, text=name)
            entry = DigitEntry(frame_fonts, justify=tk.RIGHT, width=8, textvariable=var)

            label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
            entry.grid(row=row, column=1, sticky=tk.E, padx=10, pady=5)

            row += 1

        frame_fonts.pack(side=tk.TOP, padx=5, pady=5, expand=tk.TRUE, fill=tk.BOTH)

    def get_config(self):
        font_family = self.font_config['Family'].get()
        size_main = self.font_config['Size'].get()
        size_title = self.font_config['Title Size'].get()
        size_sep =self.font_config['Separator Size'].get() 

        return {
            'workspace': {k: v.get() for k,v in self.config.items()},
            'fonts': {
                'main': f'"{font_family}" {size_main}',
                'title': f'"{font_family}" {size_title} bold',
                'separator': f'"{font_family}" {size_sep}',
            }
        }