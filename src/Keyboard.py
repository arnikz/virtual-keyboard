import sys
import tkinter as tk
from tkinter import messagebox
from ahk import AHK
from ahk import Window

class KeyboardApp:
    def __init__(self, target_hwnd=None, portrait=False):
        self.ahk = AHK(executable_path=".\\AutoHotKey.exe")
        self.target_hwnd = target_hwnd
        self.shift = False
        self.max_len = 30
        self.current_text = ""
        self.portrait = portrait

        self.root = tk.Tk()
        self.root.title("Keyboard")
        self.root.attributes('-topmost', True)
        self.root.configure(bg='white')
        self.root.resizable(False, False)

        self.letter_buttons = []
        self.setup_gui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def setup_gui(self):
        # Define layout parameters
        if self.portrait:
            key_width = 4
            key_height = 1
            font_size = 10
            gap = 1
            pad_x = 5
            pad_y = 5
        else:
            key_width = 6
            key_height = 2
            font_size = 12
            gap = 2
            pad_x = 10
            pad_y = 10

        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(padx=pad_x, pady=pad_y, fill='both', expand=True)

        # Top row: Display and Clear
        top_frame = tk.Frame(main_frame, bg='white')
        top_frame.pack(fill='x', pady=(0, 10))

        self.display_var = tk.StringVar()
        self.display = tk.Entry(top_frame, textvariable=self.display_var,
                                state='readonly', font=('TkFixedFont', font_size+2),
                                relief='sunken', bd=2)
        self.display.pack(side='left', fill='x', expand=True, padx=(0, 10), ipady=5)

        clear_btn = tk.Button(top_frame, text="Clear", font=('TkDefaultFont', font_size),
                             relief='raised', bd=2, width=8,
                             command=self.clear_text)
        clear_btn.pack(side='right', ipady=5)

        # Keyboard grid
        keyboard_frame = tk.Frame(main_frame, bg='white')
        keyboard_frame.pack()

        # Helper function to create buttons
        def make_btn(text, col, row, colspan=1, rowspan=1, is_letter=False, extra_cmd=None):
            btn = tk.Button(keyboard_frame, text=text,
                           font=('TkDefaultFont', font_size),
                           width=key_width, height=key_height,
                           relief='raised', bd=2)
            if is_letter:
                btn.orig = text.upper() if text.isalpha() else text
                btn.config(command=lambda b=btn: self.on_char_click(b))
                self.letter_buttons.append(btn)
            else:
                btn.config(command=extra_cmd)
            btn.grid(row=row, column=col, columnspan=colspan, rowspan=rowspan,
                     padx=gap, pady=gap, sticky='nsew')
            return btn

        # Row 0: Numbers
        for col, num in enumerate("1234567890"):
            make_btn(num, col, 0, is_letter=True)

        make_btn("←", 10, 0, colspan=2, extra_cmd=self.backspace)

        # Row 1: QWERTY
        for col, char in enumerate("QWERTYUIOP", start=1):
            make_btn(char, col, 1, is_letter=True)

        make_btn("Enter", 11, 1, colspan=2, rowspan=2, extra_cmd=self.submit_text)

        # Row 2: ASDF
        for col, char in enumerate("ASDFGHJKL", start=2):
            make_btn(char, col, 2, is_letter=True)

        # Row 3: Shift + ZXCV
        make_btn("Shift", 0, 3, colspan=2, extra_cmd=self.toggle_shift)
        for col, char in enumerate("ZXCVBNM.-", start=2):
            make_btn(char, col, 3, is_letter=True)

        # Row 4: Space
        make_btn("Space", 3, 4, colspan=6, extra_cmd=self.add_space)

        # Configure grid columns (weight=1 for even width)
        num_cols = 12
        for col in range(num_cols):
            keyboard_frame.grid_columnconfigure(col, weight=1, uniform='col')

        # IMPORTANT: Remove row weights to avoid extra vertical space
        for row in range(5):
            keyboard_frame.grid_rowconfigure(row, weight=0)

        # Compute the exact required size
        self.root.update_idletasks()
        req_width = keyboard_frame.winfo_reqwidth()
        req_height = keyboard_frame.winfo_reqheight()
        top_height = top_frame.winfo_reqheight()
        # Add padding and some margin
        total_width = req_width + 2 * pad_x
        total_height = req_height + top_height + 2 * pad_y + 10  # small margin

        # Set window size and center
        self.root.geometry(f'{total_width}x{total_height}')
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - total_width) // 2
        y = (screen_height - total_height) // 2
        self.root.geometry(f'+{x}+{y}')

    # All other methods remain unchanged from the previous working version
    def on_char_click(self, btn):
        if len(self.current_text) >= self.max_len:
            return
        char = btn.orig
        if self.shift:
            if char == "-":
                char = "_"
            elif char == ".":
                char = ">"
            else:
                char = char.upper()
        else:
            char = char.lower()
        self.current_text += char
        self.display_var.set(self.current_text)

    def add_space(self):
        if len(self.current_text) >= self.max_len:
            return
        self.current_text += " "
        self.display_var.set(self.current_text)

    def toggle_shift(self):
        self.shift = not self.shift
        for btn in self.letter_buttons:
            char = btn.orig
            if self.shift:
                if char == "-":
                    btn.config(text="_")
                elif char == ".":
                    btn.config(text=">")
                else:
                    btn.config(text=char.upper())
            else:
                if char == "-":
                    btn.config(text="-")
                elif char == ".":
                    btn.config(text=".")
                else:
                    btn.config(text=char.lower())

    def backspace(self):
        if len(self.current_text) > 0:
            self.current_text = self.current_text[:-1]
            self.display_var.set(self.current_text)

    def clear_text(self):
        self.current_text = ""
        self.display_var.set("")

    def submit_text(self):
        if not self.current_text:
            return
        if not self.target_hwnd:
            messagebox.showerror("Error", "No target HWND!")
            return
        try:
            import ctypes
            from ctypes import wintypes
            data = self.current_text
            size = (len(data) + 1) * 2
            class COPYDATASTRUCT(ctypes.Structure):
                _fields_ = [
                    ('dwData', wintypes.ULONG_PTR),
                    ('cbData', wintypes.DWORD),
                    ('lpData', ctypes.c_void_p)
                ]
            buffer = ctypes.create_unicode_buffer(data)
            cds = COPYDATASTRUCT()
            cds.dwData = 1
            cds.cbData = size
            cds.lpData = ctypes.addressof(buffer)
            win = Window.from_id(self.target_hwnd, ahk=self.ahk)
            win.send_message(0x4A, 0, ctypes.addressof(cds))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send message: {e}")
            return
        self.root.quit()
        sys.exit()

    def on_cancel(self):
        if self.target_hwnd:
            try:
                import ctypes
                from ctypes import wintypes
                class COPYDATASTRUCT(ctypes.Structure):
                    _fields_ = [
                        ('dwData', wintypes.ULONG_PTR),
                        ('cbData', wintypes.DWORD),
                        ('lpData', ctypes.c_void_p)
                    ]
                cds = COPYDATASTRUCT()
                cds.dwData = 2
                cds.cbData = 0
                cds.lpData = 0
                win = Window.from_id(self.target_hwnd, ahk=self.ahk)
                win.send_message(0x4A, 0, ctypes.addressof(cds))
            except Exception:
                pass
        self.root.quit()
        sys.exit()

    def run(self):
        self.root.mainloop()

def main():
    target_hwnd = None
    portrait = False
    for arg in sys.argv[1:]:
        if arg in ('--portrait', '-p'):
            portrait = True
        elif arg.isdigit():
            target_hwnd = int(arg)
    app = KeyboardApp(target_hwnd, portrait)
    app.run()

if __name__ == "__main__":
    main()
