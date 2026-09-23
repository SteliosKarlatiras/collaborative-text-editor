import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter import filedialog
from tkinter import font
from tkinter import colorchooser
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import Comments_clean_ui as cmt
import os
import io
import webbrowser
import json
import copy



class MyApp():

    def __init__(self, root):
        self.root = root

        # ---------- Application window ----------
        self.BG = '#F4F6F8'
        self.SURFACE = '#FFFFFF'
        self.BORDER = '#D9E0E7'
        self.TEXT = '#1F2937'
        self.MUTED = '#6B7280'
        self.ACCENT = '#2563EB'
        self.ACCENT_HOVER = '#1D4ED8'
        self.DANGER = '#DC2626'

        self.root.configure(bg=self.BG)
        self.root.title('Collaborative Text Annotator')
        self.root.minsize(900, 600)
        try:
            self.root.state('zoomed')
        except tk.TclError:
            self.root.geometry('1200x780')

        self.pc = os.environ.get('HOME') or os.path.expanduser('~')

        # ---------- Application data ----------
        self.Usernametuple = []
        self.bill_list = []
        self.A = {}
        self.Colors = [
            'yellow', 'orange', 'light sky blue', 'light green', 'light pink', 'light blue',
            'light cyan', 'light sea green', 'light goldenrod yellow', 'light yellow', 'light salmon',
            'light coral', 'LightSkyBlue1', 'LightSkyBlue2', 'LightSkyBlue3', 'LightBlue1',
            'LightBlue2', 'LightCyan2', 'LightCyan3', 'LightYellow2', 'LightYellow3',
            'LightSalmon2', 'LightPink1', 'LightPink2', 'LightPink3'
        ]
        self.color_letters = {}
        self.sorted_list = []
        self.text_file = None
        self.name = None
        self.open_status = False
        self.save_status = True
        self._saved_snapshot = None

        # ---------- ttk styling ----------
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass

        style.configure(
            'Toolbar.TButton',
            font=('Segoe UI', 10),
            padding=(12, 7),
            background=self.SURFACE,
            foreground=self.TEXT,
            borderwidth=1,
            relief='flat'
        )
        style.map(
            'Toolbar.TButton',
            background=[('active', '#EAF0FF')],
            foreground=[('active', self.ACCENT)]
        )
        style.configure(
            'Primary.TButton',
            font=('Segoe UI Semibold', 10),
            padding=(14, 8),
            background=self.ACCENT,
            foreground='white',
            borderwidth=0
        )
        style.map(
            'Primary.TButton',
            background=[('active', self.ACCENT_HOVER), ('pressed', self.ACCENT_HOVER)]
        )
        style.configure('Clean.TCombobox', padding=6)

        # ---------- Top bar ----------
        self.toolbar_frame = tk.Frame(
            root,
            bg=self.SURFACE,
            highlightthickness=1,
            highlightbackground=self.BORDER,
            height=58
        )
        self.toolbar_frame.pack(fill='x', side='top')
        self.toolbar_frame.pack_propagate(False)

        title_area = tk.Frame(self.toolbar_frame, bg=self.SURFACE)
        title_area.pack(side='left', padx=(18, 20), pady=8)
        tk.Label(
            title_area,
            text='Text Annotator',
            bg=self.SURFACE,
            fg=self.TEXT,
            font=('Segoe UI Semibold', 14)
        ).pack(anchor='w')
        tk.Label(
            title_area,
            text='Collaborative annotation editor',
            bg=self.SURFACE,
            fg=self.MUTED,
            font=('Segoe UI', 8)
        ).pack(anchor='w')

        self.new_button = ttk.Button(
            self.toolbar_frame,
            text='New',
            style='Toolbar.TButton',
            command=self.create_new
        )
        self.new_button.pack(side='left', padx=(0, 4), pady=10)

        self.open_button = ttk.Button(
            self.toolbar_frame,
            text='Open',
            style='Toolbar.TButton',
            command=self.open_new
        )
        self.open_button.pack(side='left', padx=4, pady=10)

        self.save_button = ttk.Button(
            self.toolbar_frame,
            text='Save',
            style='Toolbar.TButton',
            command=self.save_file
        )
        self.save_button.pack(side='left', padx=4, pady=10)

        separator = tk.Frame(self.toolbar_frame, bg=self.BORDER, width=1, height=28)
        separator.pack(side='left', padx=12, pady=15)

        self.comment_button = ttk.Button(
            self.toolbar_frame,
            text='Add comment',
            style='Primary.TButton',
            command=self.Frm
        )
        self.comment_button.pack(side='left', padx=(0, 12), pady=10)

        # User selector
        self.user_area = tk.Frame(self.toolbar_frame, bg=self.SURFACE)
        self.user_area.pack(side='left', padx=(4, 10), pady=7)
        tk.Label(
            self.user_area,
            text='User',
            bg=self.SURFACE,
            fg=self.MUTED,
            font=('Segoe UI', 8)
        ).pack(anchor='w')
        self.combo = ttk.Combobox(
            self.user_area,
            state='readonly',
            values=tuple(self.Usernametuple),
            width=18,
            style='Clean.TCombobox'
        )
        self.combo.bind('<<ComboboxSelected>>', self.namelist)
        self.combo.pack(anchor='w')

        self.com_button = ttk.Button(
            self.toolbar_frame,
            text='Show comments',
            style='Toolbar.TButton',
            command=self.open_com
        )
        self.com_button.pack(side='right', padx=(6, 18), pady=10)

        # ---------- Main workspace ----------
        self.my_frame = tk.Frame(root, bg=self.BG)
        self.my_frame.pack(padx=18, pady=(16, 10), expand=True, fill='both')

        # Comment panel (hidden initially)
        self.cmnt_frame = tk.Frame(
            self.my_frame,
            width=320,
            bg=self.SURFACE,
            highlightthickness=1,
            highlightbackground=self.BORDER
        )
        self.cmnt_frame.pack_propagate(False)

        comment_header = tk.Frame(self.cmnt_frame, bg=self.SURFACE)
        comment_header.pack(fill='x', padx=14, pady=(14, 8))
        tk.Label(
            comment_header,
            text='Comments',
            bg=self.SURFACE,
            fg=self.TEXT,
            font=('Segoe UI Semibold', 12)
        ).pack(side='left')

        self.box_comment = ScrolledText(
            self.cmnt_frame,
            width=36,
            bg=self.SURFACE,
            fg=self.TEXT,
            relief='flat',
            borderwidth=0,
            padx=8,
            pady=8,
            state='disabled'
        )
        self.box_comment.pack(side='top', fill='both', expand=True, padx=8, pady=(0, 8))

        # Editor surface
        self.editor_frame = tk.Frame(
            self.my_frame,
            bg=self.SURFACE,
            highlightthickness=1,
            highlightbackground=self.BORDER
        )
        self.editor_frame.pack(side='left', expand=True, fill='both')

        self.text_scroll = ttk.Scrollbar(self.editor_frame, orient='vertical')
        self.text_scroll.pack(side='right', fill='y')

        self.horizontal_scroll = ttk.Scrollbar(self.editor_frame, orient='horizontal')
        self.horizontal_scroll.pack(side='bottom', fill='x')

        self.my_text = tk.Text(
            self.editor_frame,
            font=('Segoe UI', 13),
            bg=self.SURFACE,
            fg=self.TEXT,
            insertbackground=self.TEXT,
            selectbackground='#BFD3FF',
            selectforeground=self.TEXT,
            undo=True,
            yscrollcommand=self.text_scroll.set,
            wrap='word',
            xscrollcommand=self.horizontal_scroll.set,
            relief='flat',
            borderwidth=0,
            padx=28,
            pady=24,
            spacing1=2,
            spacing3=2,
            exportselection=False
        )
        self.my_text.pack(side='left', expand=True, fill='both')

        self.text_scroll.config(command=self.my_text.yview)
        self.horizontal_scroll.config(command=self.my_text.xview)

        # ---------- Menu ----------
        self.my_menu = Menu(root, tearoff=False)
        self.root.config(menu=self.my_menu)

        self.file_menu = Menu(self.my_menu, tearoff=False)
        self.my_menu.add_cascade(label='File', menu=self.file_menu)
        self.file_menu.add_command(label='New    Ctrl+N', command=self.create_new)
        self.file_menu.add_command(label='Open    Ctrl+O', command=self.open_new)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Save    Ctrl+S', command=self.save_file)
        self.file_menu.add_command(label='Save As    Ctrl+F', command=self.save_as_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Exit    Esc', command=self.escape)

        self.edit_menu = Menu(self.my_menu, tearoff=False)
        self.my_menu.add_cascade(label='Edit', menu=self.edit_menu)
        self.edit_menu.add_command(label='Cut    Ctrl+X', command=lambda: self.cut_text(False))
        self.edit_menu.add_command(label='Copy    Ctrl+C', command=lambda: self.copy_text(False))
        self.edit_menu.add_command(label='Paste    Ctrl+V', command=lambda: self.paste_text(False))
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label='Undo    Ctrl+Z', command=self.my_text.edit_undo)
        self.edit_menu.add_command(label='Redo    Ctrl+Y', command=self.my_text.edit_redo)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label='Select All    Ctrl+A', command=self.select_all)
        self.edit_menu.add_command(label='Delete', command=self.deleteonly)
        self.edit_menu.add_command(label='Delete All', command=self.deleteall)

        self.search_menu = Menu(self.my_menu, tearoff=False)
        self.my_menu.add_cascade(label='Search', menu=self.search_menu)
        self.search_menu.add_command(label='Google', command=self.googlesearch)

        self.email_menu = Menu(self.my_menu, tearoff=False)
        self.my_menu.add_cascade(label='E-mail', menu=self.email_menu)
        self.email_menu.add_command(label='Gmail', command=self.gmail)
        self.email_menu.add_command(label='Outlook', command=self.Outlook)
        self.email_menu.add_command(label='Yahoo', command=self.Yahoo)

        # ---------- Status bar ----------
        self.status_bar = tk.Label(
            root,
            text='Ready',
            anchor='w',
            bg=self.SURFACE,
            fg=self.MUTED,
            font=('Segoe UI', 9),
            padx=18,
            pady=8,
            highlightthickness=1,
            highlightbackground=self.BORDER
        )
        self.status_bar.pack(fill='x', side='bottom')

        # ---------- Key bindings ----------
        self.root.bind('<Escape>', self.escape)
        self.root.bind('<Control-n>', self.create_new)
        self.root.bind('<Control-o>', self.open_new)
        self.root.bind('<Control-s>', self.save_file)
        self.root.bind('<Control-f>', self.save_as_file)
        self.root.bind('<Control-a>', self.select_all)
        self.my_text.bind('<Button-3>', RightClicker)
        self._saved_snapshot = self._current_project_data()

    #Popup Message Box Function
    def mess(self):
        self.response = messagebox.askyesno("Warning!", "You are about to close your window.\n Any unsaved changes will be lost!\n Do you want to proceed?")
        if self.response == 1:
            self.root.destroy()
    def mess_new(self):
        self.response = messagebox.askyesno("Warning!", "You are about to create a new file.\n Any unsaved changes will be lost!\n Do you want to proceed?")
        if self.response == 1:
            self.new_file()    

    def mess_open(self):
        self.response = messagebox.askyesno("Warning!", "You are about to open a file.\n Any unsaved changes will be lost!\n Do you want to proceed?")
        if self.response == 1:
            self.open_file()

    def open_com(self):
        self.cmnt_frame.pack(side='right', fill='y', padx=(12, 0))
        self.com_button.configure(command = self.close_com)
        self.com_button.configure(text='Hide comments')
        
    def close_com(self):
        self.cmnt_frame.pack_forget()
        self.com_button.configure(command = self.open_com)
        self.com_button.configure(text='Show comments')

    #New File Function
    def new_file(self):
        self.my_text.delete('1.0', 'end')
        self.root.title('Collaborative Text Annotator - Untitled')
        self.status_bar.config(text='New project')
        self.text_file = None
        self.name = None
        self.open_status = False
        self.save_status = True
        self._reset_annotation_data()
        self._saved_snapshot = self._current_project_data()

    def check(self, fake_open, fakestuff, fakeUsernametuple, fakebill_list, fakesorted_list, fakecolor_letters, fakeA):
        text=[]
        colors=[]
        textt=[]
        colorss=[]
        billname=[]
        billlist=[]
        for line in fake_open:
            #Load Usernametuple
            if line.count('&~|')!=0:
                fakeUsernametuple=line.split('&~|')
                fakeUsernametuple.remove('')
                p=fakeUsernametuple[-1].replace('\n', '')
                fakeUsernametuple.pop()
                fakeUsernametuple.append(p)
            #The correct text
            if line.count('&~|')==0  and line.count('======|')==0 and line.count('±¢')==0 and line.count('௹')==0 and line.count('۞')==0 and line.count('¶')==0 and line.count('☼')==0 and line.count('Œ')==0 and line.count('╚')==0 :
                fakestuff+=line
            #Load bill list
            if line.count('±¢')!=0:
                l=[]
                li=[]
                l=line.split('±¢')
                l.remove('')
                for i in l:
                    li=i.split('╫')
                    p=li[-1].replace('\n', '')
                    li.pop()
                    li.append(p)
                fakebill_list.append(li)
            #Load color-letters dict and A dict
            if line.count('௹')==1:
                p=line.split('௹')[-1]
                p=p.replace('\n', '')
                text.append(p)
            if line.count('۞')==1:
                p=line.split('۞')[-1]
                p=p.replace('\n', '')
                colors.append(p)
            if line.count('¶')==1:
                p=line.split("¶")[-1]
                p=p.replace('\n', '')
                textt.append(p)
            if line.count('☼')==1:
                p=line.split("☼")[-1]
                p=p.replace('\n', '') 
                colorss.append(p)
            #Load sorted list
            if line.count('Œ')!=0 and line.count('╚')!=0:
                billname=line.split('Œ')
                billname.remove('')
                billlist=billname[1].split('╚')
                billlist.remove('')
                p=billlist[-1].replace('\n','')  
                billlist.pop()
                billlist.append(p)
                fakesorted_list.append([billname[0],billlist])
        fakecolor_letters={text[n] : colors[n] for n in range(len(text))}
        fakeA={textt[n] : colorss[n] for n in range(len(textt))}
        return fakeUsernametuple, fakebill_list, fakesorted_list, fakecolor_letters, fakeA, fakestuff


    def _reset_annotation_data(self):
        self.Usernametuple = []
        self.bill_list = []
        self.sorted_list = []
        self.color_letters = {}
        self.A = {}
        self.Colors = [
            'yellow', 'orange', 'light sky blue', 'light green', 'light pink', 'light blue',
            'light cyan', 'light sea green', 'light goldenrod yellow', 'light yellow', 'light salmon',
            'light coral', 'LightSkyBlue1', 'LightSkyBlue2', 'LightSkyBlue3', 'LightBlue1',
            'LightBlue2', 'LightCyan2', 'LightCyan3', 'LightYellow2', 'LightYellow3',
            'LightSalmon2', 'LightPink1', 'LightPink2', 'LightPink3'
        ]
        self.combo.configure(values=())
        self.combo.set('')
        self.box_comment.configure(state='normal')
        self.box_comment.delete('1.0', 'end')
        self.box_comment.configure(state='disabled')

    def _tag_ranges_for(self, selected_text, color):
        tag_name = 'colored{}{}'.format(selected_text, color)
        ranges = self.my_text.tag_ranges(tag_name)
        result = []
        for i in range(0, len(ranges), 2):
            result.append({
                'start': str(ranges[i]),
                'end': str(ranges[i + 1])
            })
        return result

    def _current_project_data(self):
        highlights = []
        for selected_text, color in self.color_letters.items():
            highlights.append({
                'text': selected_text,
                'color': color,
                'ranges': self._tag_ranges_for(selected_text, color)
            })

        comments = []
        for item in self.bill_list:
            if len(item) >= 3:
                comment, user, selected_text = item[:3]
                color = self.A.get(user, 'yellow')
                comments.append({
                    'comment': comment,
                    'user': user,
                    'selected_text': selected_text,
                    'ranges': self._tag_ranges_for(selected_text, color)
                })

        return {
            'format': 'CollaborativeTextAnnotator',
            'version': 2,
            'text': self.my_text.get('1.0', 'end-1c'),
            'users': [
                {'name': name, 'color': self.A.get(name)}
                for name in self.Usernametuple
            ],
            'comments': comments,
            'highlights': highlights,
            'sorted_comments': copy.deepcopy(self.sorted_list)
        }

    def _apply_highlight(self, selected_text, color, ranges):
        tag_name = 'colored{}{}'.format(selected_text, color)
        applied = False
        for r in ranges or []:
            try:
                self.my_text.tag_add(tag_name, r['start'], r['end'])
                applied = True
            except (tk.TclError, KeyError, TypeError):
                pass

        # Compatibility fallback for projects without stored positions.
        if not applied and selected_text:
            start = self.my_text.search(selected_text, '1.0', stopindex='end')
            if start:
                end = self.my_text.index(f'{start}+{len(selected_text)}c')
                self.my_text.tag_add(tag_name, start, end)

        self.my_text.tag_config(tag_name, font=('Segoe UI', 13), background=color)

    def _load_json_project(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if data.get('format') != 'CollaborativeTextAnnotator':
            raise ValueError('This JSON file is not a Text Annotator project.')

        self.my_text.delete('1.0', 'end')
        self._reset_annotation_data()
        self.my_text.insert('1.0', data.get('text', ''))

        for user in data.get('users', []):
            name = user.get('name', '')
            color = user.get('color') or 'yellow'
            if name:
                self.Usernametuple.append(name)
                self.A[name] = color

        self.bill_list = [
            [c.get('comment', ''), c.get('user', ''), c.get('selected_text', '')]
            for c in data.get('comments', [])
        ]
        self.sorted_list = data.get('sorted_comments', [])

        for h in data.get('highlights', []):
            selected_text = h.get('text', '')
            color = h.get('color', 'yellow')
            if selected_text:
                self.color_letters[selected_text] = color
                self._apply_highlight(selected_text, color, h.get('ranges', []))

        # If an older JSON project has comments but no highlights section.
        if not data.get('highlights'):
            for c in data.get('comments', []):
                selected_text = c.get('selected_text', '')
                user = c.get('user', '')
                color = self.A.get(user, 'yellow')
                if selected_text:
                    self.color_letters[selected_text] = color
                    self._apply_highlight(selected_text, color, c.get('ranges', []))

        used_colors = set(self.A.values())
        self.Colors = [c for c in self.Colors if c not in used_colors]
        self.combo.configure(values=tuple(self.Usernametuple))

        for comment, user, selected_text in self.bill_list:
            cmt.Comment(
                self.box_comment, user, comment, self.A.get(user, 'yellow'),
                self.my_text, self.bill_list, self.color_letters,
                selected_text, self.sorted_list
            )

        self._saved_snapshot = copy.deepcopy(self._current_project_data())
        self.save_status = True

    def _load_legacy_project(self, path):
        # Imports the original custom .txt format used by the old project.
        self.my_text.delete('1.0', 'end')
        self._reset_annotation_data()
        stuff = ''
        with io.open(path, 'r', encoding='utf-8') as old_file:
            (self.Usernametuple, self.bill_list, self.sorted_list,
             self.color_letters, self.A, stuff) = self.check(
                old_file, stuff, [], [], [], {}, {}
            )

        self.my_text.insert('1.0', stuff.rstrip('\n'))
        used_colors = set(self.A.values())
        self.Colors = [c for c in self.Colors if c not in used_colors]

        # Recreate highlights using the legacy selected-text information.
        for selected_text, color in self.color_letters.items():
            start = '1.0'
            while True:
                found = self.my_text.search(selected_text, start, stopindex='end')
                if not found:
                    break
                end = self.my_text.index(f'{found}+{len(selected_text)}c')
                tag_name = 'colored{}{}'.format(selected_text, color)
                self.my_text.tag_add(tag_name, found, end)
                self.my_text.tag_config(tag_name, font=('Segoe UI', 13), background=color)
                start = end

        self.combo.configure(values=tuple(self.Usernametuple))
        for comment, user, selected_text in self.bill_list:
            cmt.Comment(
                self.box_comment, user, comment, self.A.get(user, 'yellow'),
                self.my_text, self.bill_list, self.color_letters,
                selected_text, self.sorted_list
            )

        # Legacy files are imported, not overwritten. First Save will ask for .cta.
        self.text_file = None
        self.name = None
        self.open_status = False
        self._saved_snapshot = copy.deepcopy(self._current_project_data())
        self.save_status = True
        self.root.title('Collaborative Text Annotator - Imported legacy project')
        self.status_bar.config(text='Legacy project imported — save it as a new .cta project')

    def _has_unsaved_changes(self):
        if self._saved_snapshot is None:
            return bool(self.my_text.get('1.0', 'end-1c') or self.bill_list)
        return self._current_project_data() != self._saved_snapshot

    def _confirm_discard_changes(self, action_text):
        if not self._has_unsaved_changes():
            return True
        return messagebox.askyesno(
            'Unsaved changes',
            f'You have unsaved changes. Do you want to {action_text} without saving?'
        )

    def _write_json_project(self, path):
        data = self._current_project_data()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self._saved_snapshot = copy.deepcopy(data)
        self.save_status = True

    #Open Files Function
    def open_file(self):
        path = filedialog.askopenfilename(
            initialdir=self.pc,
            title='Open project',
            filetypes=(
                ('Text Annotator Projects', '*.cta'),
                ('JSON Projects', '*.json'),
                ('Legacy Text Annotator Files', '*.txt'),
                ('All Files', '*.*')
            )
        )
        if not path:
            return

        try:
            if path.lower().endswith(('.cta', '.json')):
                self._load_json_project(path)
                self.text_file = path
                self.name = os.path.basename(path)
                self.open_status = True
                self.root.title(f'Collaborative Text Annotator - {self.name}')
                self.status_bar.config(text=f'Opened: {self.name}')
            else:
                # Try JSON first even if the extension is unusual, then legacy format.
                try:
                    self._load_json_project(path)
                    self.text_file = path
                    self.name = os.path.basename(path)
                    self.open_status = True
                    self.root.title(f'Collaborative Text Annotator - {self.name}')
                    self.status_bar.config(text=f'Opened: {self.name}')
                except (json.JSONDecodeError, ValueError, UnicodeDecodeError):
                    self._load_legacy_project(path)
        except Exception as exc:
            messagebox.showerror('Open project', f'Could not open the project:\n\n{exc}')

    def save_as_file(self, *args):
        path = filedialog.asksaveasfilename(
            defaultextension='.cta',
            initialdir=self.pc,
            title='Save Text Annotator Project',
            filetypes=(
                ('Text Annotator Project', '*.cta'),
                ('JSON Project', '*.json')
            )
        )
        if not path:
            return

        try:
            self._write_json_project(path)
            self.text_file = path
            self.name = os.path.basename(path)
            self.open_status = True
            self.root.title(f'Collaborative Text Annotator - {self.name}')
            self.status_bar.config(text=f'Saved: {self.name}')
        except Exception as exc:
            messagebox.showerror('Save project', f'Could not save the project:\n\n{exc}')

    def escape(self, *args):
        if self._confirm_discard_changes('exit'):
            self.root.destroy()

    def create_new(self, *args):
        if self._confirm_discard_changes('create a new project'):
            self.new_file()

    def open_new(self, *args):
        if self._confirm_discard_changes('open another project'):
            self.open_file()

    def save_file(self, *args):
        if not self.text_file:
            self.save_as_file()
            return

        try:
            self._write_json_project(self.text_file)
            self.name = os.path.basename(self.text_file)
            self.open_status = True
            self.status_bar.config(text=f'Saved: {self.name}')
        except Exception as exc:
            messagebox.showerror('Save project', f'Could not save the project:\n\n{exc}')

    def cut_text(self,f):
        if self.my_text.selection_get():
            self.selected = self.my_text.selection_get()
            self.my_text.delete("sel.first", "sel.last")
            self.root.clipboard_clear()
            self.root.clipboard_append(self.selected)


    #Copy Text
    def copy_text(self,f):
        if self.my_text.selection_get():
            self.selected = self.my_text.selection_get()
            self.root.clipboard_clear()
            self.root.clipboard_append(self.selected)



    #Paste Text
    def paste_text(self,f):
        if self.selected:
            self.position = self.my_text.index(INSERT)
            self.my_text.insert(self.position, self.selected)
    
    def deleteall(self):
        self.my_text.delete("1.0", 'end')

    def select_all(self, *args):
        self.my_text.tag_add('sel', 1.0, 'end')
    
    def deleteonly(self):
        if self.my_text.selection_get():
            self.my_text.delete("sel.first", "sel.last")

    #Tou steliou ta def
    def googlesearch(self):
        webbrowser.open("https://www.google.com/?#q=")
 
    def gmail(self):
        webbrowser.open("https://www.google.com/intl/el/gmail/about/")

    def Outlook(self):
        webbrowser.open("https://www.msn.com/el-gr/?ocid=mailsignout&pc=U591")

    def Yahoo(self):
        webbrowser.open("https://gr.yahoo.com/")

    def google_search(self):
        self.selected = self.my_text.selection_get()         
        webbrowser.open("https://www.google.com/?#q="+self.selected)  

    def selectall(self, *args):
        self.my_text.tag_add('sel', '1.0', 'end')
        return "break"

    def mini(self):
        k=[]
        for i in self.A.values():
            k.append(i)
        for i in k:
            self.Colors.remove(i)

    def Frm(self):
        # Store both the selected text and its exact indexes BEFORE
        # opening another window. This keeps comments reliable even when
        # focus moves from the editor to the toolbar/comment dialog.
        try:
            self.selection_start = self.my_text.index('sel.first')
            self.selection_end = self.my_text.index('sel.last')
            self.selected = self.my_text.get(self.selection_start, self.selection_end)
        except tk.TclError:
            messagebox.showinfo('Add comment', 'Select some text first, then click Add comment.')
            return

        if not self.selected.strip():
            messagebox.showinfo('Add comment', 'Select some text first, then click Add comment.')
            return

        self.x = tk.Toplevel(self.root)
        self.x.title('Add comment')
        self.x.geometry('520x230+500+160')
        self.x.resizable(False, False)
        self.x.configure(bg=self.BG)
        self.x.transient(self.root)
        self.x.grab_set()
        self.x.bind('<Button-3>', MiniRightClick)

        self.frm1 = tk.Frame(self.x, bg=self.SURFACE, padx=22, pady=18)
        self.frm = tk.Frame(self.x, bg=self.SURFACE, padx=22, pady=0)
        self.userLabel = tk.Label(
            self.frm1, bg=self.SURFACE, fg=self.TEXT,
            text='Username', font=('Segoe UI Semibold', 10)
        )
        self.titleLabel = tk.Label(
            self.frm1, bg=self.SURFACE, fg=self.TEXT,
            text='Comment', font=('Segoe UI Semibold', 10)
        )
        self.userCombo = ttk.Combobox(
            self.frm1, font=('Segoe UI', 11),
            values=tuple(self.Usernametuple), width=30
        )
        if self.Usernametuple:
            self.userCombo.set(self.Usernametuple[-1])

        self.title_Entry = tk.Entry(
            self.frm1, font=('Segoe UI', 11), bg='white',
            fg=self.TEXT, relief='solid', borderwidth=1, width=32
        )
        self.buttonConfirm = ttk.Button(
            self.frm, text='Add comment',
            style='Primary.TButton', command=self.Confirm
        )

        self.frm1.pack(fill='both', expand=True, padx=12, pady=(12, 0))
        self.frm1.grid_columnconfigure(1, weight=1)
        self.userLabel.grid(row=0, column=0, pady=(0, 12), padx=(0, 18), sticky='w')
        self.userCombo.grid(row=0, column=1, pady=(0, 12), sticky='ew')
        self.titleLabel.grid(row=1, column=0, pady=0, padx=(0, 18), sticky='w')
        self.title_Entry.grid(row=1, column=1, pady=0, sticky='ew')
        self.frm.pack(fill='x', padx=12, pady=(0, 12))
        self.buttonConfirm.pack(pady=(0, 4), side='right')

        self.title_Entry.focus_set()
        self.x.bind('<Return>', lambda event: self.Confirm())

    def Confirm(self):
        self.title = self.title_Entry.get().strip()
        self.username = self.userCombo.get().strip()

        if not self.username:
            messagebox.showwarning('Add comment', 'Please enter a username.', parent=self.x)
            self.userCombo.focus_set()
            return

        if not self.title:
            messagebox.showwarning('Add comment', 'Please write a comment.', parent=self.x)
            self.title_Entry.focus_set()
            return

        if self.Usernametuple.count(self.username) == 0:
            self.Usernametuple.append(self.username)
        else:
            self.Usernametuple.remove(self.username)
            self.Usernametuple.append(self.username)

        self.bill_list.append([self.title, self.username, self.selected])

        names = [name for name, comments in self.sorted_list]
        if self.username in names:
            for name, comments in self.sorted_list:
                if name == self.username:
                    comments.append(self.title)
                    break
        else:
            self.sorted_list.append([self.username, [self.title]])

        self.Highlight(self.selected)
        cmt.Comment(
            self.box_comment, self.username, self.title, self.A[self.username],
            self.my_text, self.bill_list, self.color_letters,
            self.selected, self.sorted_list
        )
        self.combo.configure(values=tuple(self.Usernametuple))

        # Open the comments panel automatically so the new annotation is visible.
        if not self.cmnt_frame.winfo_ismapped():
            self.open_com()

        self.x.destroy()

    def Highlight(self, x, *args):
        if self.username in self.A:
            color = self.A[self.username]
        else:
            color = self.Colors.pop(0) if self.Colors else 'yellow'
            self.A[self.username] = color

        tag_name = 'colored{}{}'.format(self.selected, color)
        self.my_text.tag_add(tag_name, self.selection_start, self.selection_end)
        self.my_text.tag_config(
            tag_name,
            font=('Segoe UI', 13),
            background=color
        )
        self.color_letters.update({x: color})

    def namelist(self, *args):
        lista=[]
        listes=[]
        self.top=tk.Toplevel(self.root)
        self.top.geometry('560x320')
        self.top.resizable(False,False)
        self.user=self.combo.get()
        self.top.title(self.user)
        self.usercomment=''
        self.bar_frame = tk.Frame(self.top,bg = self.A[self.user],height = 8,relief='sunken', borderwidth=2) #1Σβηστε αυτα αν δεν σας αρεσει το bar color frame
        self.bar_frame.pack(side = 'top',fill = 'x')                                                          #2
        # self.topframe=tk.Frame(self.top, bg=self.A[self.user], relief='sunken', borderwidth=2)                #And Uncomment this
        self.topframe=tk.Frame(self.top, bg=self.SURFACE, padx=18, pady=14)
        for i, j in self.color_letters.items():
            if j==self.A[self.user]:
                lista.append(i)
        for i in lista:
            if i.strip().count(' ')==0:
                listes.append('|Mentioned text: {}|'.format(i.strip()))
            else:
                listes.append('|Mentioned text: {}...{}|'.format( i.strip().split(' ')[0], i.strip().split(' ')[-1]))
        for i,j in self.sorted_list:
            if i==self.user:
                if j==[]:
                    self.usercomment='No comments found'
                    break
                count=0
                for a in j:
                    count+=1
                    self.usercomment+='{}) {}\n{}\n'.format(count,a, listes[count-1])
        self.toplabeltitle=tk.Label(self.topframe, text='Comments by {}'.format(self.user), bg=self.SURFACE, fg=self.TEXT, font=('Segoe UI Semibold', 15))
        self.toptext=ScrolledText(self.topframe, relief='solid', borderwidth=1, font=('Segoe UI', 11), bg='white', fg=self.TEXT, height=10, wrap='word', padx=10, pady=10)
        self.toptext.insert('end', self.usercomment)
        self.toptext.config(state='disabled')
        self.topframe.pack(expand=1, fill='both')
        self.toplabeltitle.pack(anchor='w', padx=2, pady=(0,10))
        self.toptext.pack(fill='both', expand=True, padx=2, side='top', pady=(0,2))






class RightClicker:
    def __init__(self, e):
        commands = ["Cut"]
        commands2 = ["Copy"]
        commands3 = ["Paste"]
        commands4=["Delete"]
        
        menu = tk.Menu(None, tearoff=0, takefocus=0)

        for txt in commands:
            menu.add_command(label=txt, command=lambda e=e,txt=txt:self.click_command(e,txt))

        for txt in commands2:
            menu.add_command(label=txt, command=lambda e=e,txt=txt:self.click_command2(e,txt)) 

        for txt in commands3:
            menu.add_command(label=txt, command=lambda e=e,txt=txt:self.click_command3(e,txt))

        menu.add_separator()

        menu.add_command(label="Google Search", command=app.google_search)

        menu.add_separator() 

        menu.add_command(label="Select All", command=app.selectall)

        for txt in commands4:
            menu.add_command(label=txt, command=lambda e=e,txt=txt:self.click_command4(e,txt)) 
          
                          
        menu.tk_popup(e.x_root + 40, e.y_root + 20, entry="0")

    def click_command(self, e, cmd):
        e.widget.event_generate('<<Cut>>')

    def click_command2(self, e, cmd):
        e.widget.event_generate('<<Copy>>')

    def click_command3(self, e, cmd):
        e.widget.event_generate('<<Paste>>')

    def click_command4(self, e, cmd):
        e.widget.event_generate('<Delete>')

class MiniRightClick:
    def __init__(self, event):
        right_click_menu = Menu(None, tearoff=0, takefocus=0)

        for txt in ['Cut', 'Copy', 'Paste']:
            right_click_menu.add_command(
                label=txt, command=lambda event=event, text=txt:
                self.right_click_command(event, text))

        right_click_menu.tk_popup(event.x_root + 40, event.y_root + 10, entry='0')

    def right_click_command(self, event, cmd):
        event.widget.event_generate(f'<<{cmd}>>')



if __name__ == '__main__':
    root = tk.Tk()
    app = MyApp(root)

    icon_path = os.path.join(os.path.dirname(__file__), 'logo_text_editor3.ico')
    if os.path.exists(icon_path):
        try:
            root.iconbitmap(icon_path)
        except tk.TclError:
            pass
    root.mainloop()
