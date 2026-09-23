import tkinter as tk
import textwrap


class Comment:
    def __init__(self, root, name, comment, color, text, llist, dictt, sel, sortedlist):
        self.name = name
        self.comment = comment
        self.root = root
        self.color = color
        self.text = text
        self.llist = llist
        self.dictt = dictt
        self.sel = sel
        self.sorted = sortedlist
        self.output()

    def output(self):
        # Compact card-style comment component.
        self.each_com_frame = tk.Frame(
            self.root,
            bg='#FFFFFF',
            highlightthickness=1,
            highlightbackground='#D9E0E7',
            padx=12,
            pady=10
        )

        top_row = tk.Frame(self.each_com_frame, bg='#FFFFFF')
        top_row.pack(fill='x')

        self.name_label = tk.Label(
            top_row,
            text=self.name or 'Unnamed user',
            font=('Segoe UI Semibold', 10),
            bg='#FFFFFF',
            fg='#1F2937',
            anchor='w'
        )
        self.name_label.pack(side='left', fill='x', expand=True)

        self.button = tk.Button(
            top_row,
            text='×',
            command=self.destroy,
            bg='#FFFFFF',
            fg='#9CA3AF',
            activebackground='#FEE2E2',
            activeforeground='#B91C1C',
            relief='flat',
            borderwidth=0,
            font=('Segoe UI Semibold', 11),
            cursor='hand2'
        )
        self.button.pack(side='right')

        selected_text = self.sel.strip()
        if selected_text.count(' ') == 0:
            mentioned = selected_text
        else:
            parts = selected_text.split()
            mentioned = '{} … {}'.format(parts[0], parts[-1])

        self.selectedlabel = tk.Label(
            self.each_com_frame,
            text='“{}”'.format(mentioned),
            font=('Segoe UI', 9),
            bg=self.color,
            fg='#1F2937',
            anchor='w',
            justify='left',
            padx=8,
            pady=5,
            wraplength=245
        )
        self.selectedlabel.pack(fill='x', pady=(8, 7))

        self.comment_label = tk.Label(
            self.each_com_frame,
            text=self.comment,
            font=('Segoe UI', 10),
            bg='#FFFFFF',
            fg='#374151',
            anchor='w',
            justify='left',
            wraplength=245
        )
        self.comment_label.pack(fill='x')

        self.root.configure(state='normal')
        self.root.window_create('end', window=self.each_com_frame)
        self.root.insert('end', '\n')
        self.root.configure(state='disabled')

    def destroy(self):
        self.each_com_frame.destroy()
        self.text.tag_remove('colored{}{}'.format(self.sel, self.color), 1.0, 'end')
        if [self.comment, self.name, self.sel] in self.llist:
            self.llist.remove([self.comment, self.name, self.sel])
        if self.sel in self.dictt:
            del self.dictt[self.sel]
        for name, comments in self.sorted:
            if name == self.name and self.comment in comments:
                comments.remove(self.comment)

    def commentwrap(self, text, emptystr):
        wrapped = textwrap.wrap(text, width=30)
        return '\n'.join(wrapped)
