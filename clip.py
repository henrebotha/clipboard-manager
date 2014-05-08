# Issues:
# - long clips will only show the last part of the clip. Correction will require
#   creating a Clip class that can contain both the full text of a clip, and a
#   display-friendly version
# - pasting needs implementation
# - clipboard detection is broken! it only detects the last-copied item, and
#   only when opening the window.

from tkinter import *
from time import sleep
import ctypes
from ctypes import wintypes
import win32con
import win32api

user32 = ctypes.windll.user32
byref = ctypes.byref

class Window(Tk):
    def __init__(self):
        super().__init__()
        # GUI init
        self.title("Clippy")
        self.iconbitmap("icon2.ico")
        self.geometry("250x210-0+0") # place window in NE (0 left, 0 down)
        self.resizable(FALSE,FALSE)

        # widgets & general init
        self.my_clipboard = Clipboard(self) # give clipboard reference to window
        self.clips_vars = [StringVar(i.text_display) for i in self.my_clipboard.clips]
        self.labels_clips = [Label(self, textvariable=self.clips_vars[i],
            width=30, height=1,
            anchor=W) for i in range(len(self.my_clipboard.clips))]
        self.labels_nums = [Label(self,
            text=str(i+1)[-1]+".") for i in range(10)]
        for i, n, c in zip(range(10), self.labels_nums, self.labels_clips):
            n.grid(column=0, row=i, padx=5)
            c.grid(column=1, row=i)

        # event bindings
        for i in range(10):
            s = "<Key-{}>".format(str(i+1)[-1])
            self.bind_all(s, self.my_clipboard.paste)

        self.after(1, self.hotkey_handler)

        self.my_clipboard.update_clipboard()

    def update_label(self, index, text):
        '''Change the clip at index to text and update its corresponding label.'''
        self.my_clipboard.clips[index].text = text
        self.my_clipboard.clips[index].text_display = text[-30:]
        self.clips_vars[index].set(self.my_clipboard.clips[index].text_display)

    def hotkey_handler(self):
        self.msg = wintypes.MSG()
        if user32.GetMessageA(byref(self.msg), None, 0, 0) != 0:
            if self.msg.message == win32con.WM_HOTKEY:
                if self.msg.wParam == 1:
                    self.deiconify()
        user32.TranslateMessage(byref(self.msg))
        user32.DispatchMessageA(byref(self.msg))
        self.after(1, self.hotkey_handler)


class Clipboard(object):
    def __init__(self, parent):
        self.clips = [Clip("") for i in range(10)]
        self.parent = parent

    def paste(self, event):
        i = int(event.keysym)
        if i == 0:
            i = 10
        print("Pasting: " + self.clips[i-1].text_display)

        # Implementation:
        # - on global hotkey press, find handle to current window before
        #   deiconifying this window
        # - on paste, send WM_PASTE message to said window
        
        # # http://bytes.com/topic/python/answers/646943-get-control-over-window
        # hwnd = user32.FindWindowA(None, "Notepad")
        # win32api.SendMessage(hwnd, win32con.WM_PASTE, 0, 0)
        # # http://bytes.com/topic/python/answers/646943-get-control-over-window

        event.widget.iconify()

    def update_clipboard(self):
        self.clip_buffer = self.parent.clipboard_get()
        if self.clip_buffer == None:
            self.clip_buffer = ""
        else:
            self.clip_buffer == str(self.clip_buffer) # is this necessary?
        # if self.clip_buffer in self.clips:
        i = self.find_clip(self.clip_buffer, self.clips)
        if i:
            self.clips.insert(0, self.clips.pop(i))
        else:
            self.clips.insert(0, Clip(self.clip_buffer))
            self.clips.pop()
        for i, c in enumerate(self.clips):
            self.parent.update_label(i, c.text_display)
        self.parent.after(1, self.update_clipboard)

    def find_clip(self, text, clips):
        '''Returns index of a clip if text is found and False otherwise.'''
        for i, c in enumerate(clips):
            if c.text == text:
                return i
        return False


class Clip(object):
    def __init__(self, text):
        self.text = text
        self.text_display = text[-30:]


def run():
    '''Main app code.'''
    try:
        root = Window()

        if user32.RegisterHotKey(None, 1, win32con.MOD_WIN, ord("V")) != 0:
            print("--Hotkey registered!")
        else:
            print("--Error registering hotkey.")

        # root.after(1, hotkey_handler, root) # schedule keyboard shortcut handler
        root.mainloop()
    finally:
        if user32.UnregisterHotKey(None, 1) != 0:
            print("--Hotkey deregistered!")
        else:
            print("--Error deregistering hotkey.")

if __name__ == "__main__":
    run()
