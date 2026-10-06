import sys
import ahk
import argparse
import tkinter as tk
import ctypes
from tkinter import messagebox
from ahk import AHK
from ctypes import wintypes

# Define ULONG_PTR (replaces wintypes.ULONG_PTR) and COPYDATASTRUCT globally
ULONG_PTR = ctypes.c_size_t

class COPYDATASTRUCT(ctypes.Structure):
    _fields_ = [
        ('dwData', ULONG_PTR),
        ('cbData', wintypes.DWORD),
        ('lpData', ctypes.c_void_p)
    ]

class KeyboardApp:
    BG_COLOR = '#221E1F'  # set background color
    BTN_COLOR = 'lightgray'  # set button color

    def __init__(self, hwnd=None, desc="", mode=0):
        self.ahk = AHK(executable_path="Resources\\AutoHotkey.exe")
        self.hwnd = hwnd
        self.shift = True
        self.max_len = 30
        self.desc = desc
        self.mode = mode

        self.root = tk.Tk()
        self.root.title("Virtual Keyboard")
        self.root.attributes('-topmost', True)
        self.root.configure(bg=self.BG_COLOR)
        self.root.resizable(False, False)

        self.letter_buttons = []
        self.setup_gui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def setup_gui(self):
        # Define layout parameters
        if self.mode:
            key_width = 5
            key_height = 2
            font_size = 11
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

        main_frame = tk.Frame(self.root, bg=self.BG_COLOR)
        main_frame.pack(padx=pad_x, pady=pad_y, fill='both', expand=True)

        # Top row: Display and Clear
        top_frame = tk.Frame(main_frame, bg=self.BG_COLOR)
        top_frame.pack(fill='x', pady=(0, 10))

        self.display_var = tk.StringVar()
        self.display_var.set(self.desc)

        self.display = tk.Entry(top_frame, textvariable=self.display_var,
                                state='readonly', font=('TkFixedFont', font_size+2),
                                relief='sunken', bd=2)
        self.display.pack(side='left', fill='x',
                          expand=True, padx=(0, 10), ipady=5)

        clear_btn = tk.Button(top_frame, text="Clear", font=('TkDefaultFont', font_size),
                              relief='raised', bd=2, width=8,
                              command=self.clear_text, bg=self.BTN_COLOR)
        clear_btn.pack(side='right', ipady=5)

        # Keyboard grid
        keyboard_frame = tk.Frame(main_frame, bg=self.BG_COLOR)
        keyboard_frame.pack()

        # Helper function to create buttons
        def make_btn(text, col, row, colspan=1, rowspan=1, is_letter=False, extra_cmd=None):
            btn = tk.Button(keyboard_frame, text=text,
                            font=('TkDefaultFont', font_size),
                            width=key_width, height=key_height,
                            relief='raised', bd=2, bg=self.BTN_COLOR)
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

        make_btn("Enter", 11, 1, colspan=2, rowspan=2,
                 extra_cmd=self.submit_text)

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
        if len(self.desc) >= self.max_len:
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
        self.desc += char
        self.display_var.set(self.desc)

    def add_space(self):
        if len(self.desc) >= self.max_len:
            return
        self.desc += " "
        self.display_var.set(self.desc)

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
        if len(self.desc) > 0:
            self.desc = self.desc[:-1]
            self.display_var.set(self.desc)

    def clear_text(self):
        self.desc = ""
        self.display_var.set("")

    def submit_text(self):
        if not self.desc:
            return
        if not self.hwnd:
            messagebox.showerror("Error", "No target HWND!")
            return
        try:
            data = self.desc
            size = (len(data) + 1) * 2  # UTF-16 bytes

            # Allocate memory for the string
            buffer = ctypes.create_unicode_buffer(data)

            # Create COPYDATASTRUCT
            cds = COPYDATASTRUCT()
            cds.dwData = 1
            cds.cbData = size
            cds.lpData = ctypes.addressof(buffer)

            # Call SendMessage directly via ctypes
            user32 = ctypes.windll.user32
            # HWND is a pointer-sized integer
            hwnd = wintypes.HWND(self.hwnd)
            # WM_COPYDATA = 0x004A
            user32.SendMessageW(hwnd, 0x004A, 0, ctypes.byref(cds))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send message: {e}")
            return
        self.root.quit()
        sys.exit()

    def on_cancel(self):
        if self.hwnd:
            try:
                cds = COPYDATASTRUCT()
                cds.dwData = 2  # CANCEL
                cds.cbData = 0
                cds.lpData = 0

                user32 = ctypes.windll.user32
                hwnd = wintypes.HWND(self.hwnd)
                user32.SendMessageW(hwnd, 0x004A, 0, ctypes.byref(cds))

            except Exception:
                pass
        self.root.quit()
        sys.exit()

    def run(self):
        self.root.mainloop()


def main():
    parser = argparse.ArgumentParser(description="Virtual Keyboard.", add_help=True)
    parser.add_argument("-i", "--hwnd", type=int, required=True,
                        help="Pass a unique identifier or handle to a window.")
    parser.add_argument("-d", "--desc", type=str, default="", required=False,
                        help="Include description in a file name.")
    parser.add_argument("-m", "--mode", type=int, default=0, required=False,
                        help="Show the keyboard in landscape (0) or portrait mode (1) (default: 0).")

    try:
        args = parser.parse_args()
        if args.mode not in (0, 1):
            parser.print_help()
            parser.error("Invalid value '%s' for MODE!" % args.mode)
    except SystemExit as e:
        input("Press ENTER to exit.")
    else:
        app = KeyboardApp(hwnd=args.hwnd, desc=args.desc, mode=args.mode)
        app.run()

if __name__ == "__main__":
    main()
