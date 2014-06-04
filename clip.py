# Issues:
# - Long clips will only show the last part of the clip. Correction will require
#   creating a Clip class that can contain both the full text of a clip, and a
#   display-friendly version
# - Pasting implementation only works in some apps (Notepad)
# - Lots of possibly unnecessary win32clipboard.OpenClipboard()/
#   win32clipboard.CloseClipboard() calls. See if I can't get rid of them

from tkinter import *
import ctypes
from ctypes import wintypes
import win32con
import win32api
import win32gui
import win32process
import win32clipboard

user32 = ctypes.windll.user32
byref = ctypes.byref

class GUITHREADINFO(ctypes.Structure):
    _fields_ = [
    ("cbSize", wintypes.DWORD),
    ("flags", wintypes.DWORD),
    ("hwndActive", wintypes.HWND),
    ("hwndFocus", wintypes.HWND),
    ("hwndCapture", wintypes.HWND),
    ("hwndMenuOwner", wintypes.HWND),
    ("hwndMoveSize", wintypes.HWND),
    ("hwndCaret", wintypes.HWND),
    ("rcCaret", wintypes.RECT)
    ]


class Window(Tk):
    def __init__(self):
        super().__init__()
        # GUI init
        self.title("Clippy")
        self.iconbitmap("icon2.ico")
        self.geometry("250x210-0+0") # place window in NE (0 left, 0 down)
        self.resizable(FALSE,FALSE)

        # widgets & general init
        self.my_cb = Clipboard(self) # give clipboard reference to window
        self.clips_vars = [StringVar(i) for i in self.my_cb.clips]
        self.labels_clips = [Label(self, textvariable=self.clips_vars[i],
            width=30, height=1,
            anchor=W) for i in range(len(self.my_cb.clips))]
        self.labels_nums = [Label(self,
            text=str(i+1)[-1]+".") for i in range(10)]
        for i, n, c in zip(range(10), self.labels_nums, self.labels_clips):
            n.grid(column=0, row=i, padx=5)
            c.grid(column=1, row=i)

        # event bindings
        for i in range(10):
            s = "<Key-{}>".format(str(i+1)[-1])
            self.bind_all(s, self.my_cb.paste)

        self.after(1, self.loop_functions)

    def update_label(self, index, text):
        '''Change the clip at index to text and update its corresponding label.'''
        self.my_cb.clips[index] = text
        self.clips_vars[index].set(text)

    def hotkey_handler(self):
        self.msg = wintypes.MSG()

        if user32.GetMessageA(byref(self.msg), None, 0, 0) != 0:
            if self.msg.message == win32con.WM_HOTKEY:
                if self.msg.wParam == 1:
                    gui = GUITHREADINFO(cbSize=ctypes.sizeof(GUITHREADINFO))
                    self.hwnd_foreground = win32gui.GetForegroundWindow()
                    # self.tid_foreground = win32process.GetWindowThreadProcessId(self.hwnd_foreground)[0]
                    
                    if user32.GetGUIThreadInfo(0, byref(gui)) == False:
                        print("ERROR #" + str(win32api.GetLastError()))

                    self.hwnd_focus = gui.hwndFocus
                    # self.hwnd_foreground = gui.hwndActive
                    self.after(1, self.update)
                    self.deiconify()

        user32.TranslateMessage(byref(self.msg))
        user32.DispatchMessageA(byref(self.msg))

    def loop_functions(self):
        self.hotkey_handler()
        self.my_cb.update_clipboard()
        self.after(1, self.loop_functions)


class Clipboard(object):
    def __init__(self, parent):
        self.clips = ["" for i in range(10)]
        self.parent = parent

    def paste(self, event):
        i = int(event.keysym)
        if i == 0:
            i = 10

        # store current clipboard state
        try:
            win32clipboard.OpenClipboard()
            self.clipboard_previous = win32clipboard.GetClipboardData(win32con.CF_TEXT)
        finally:
            win32clipboard.CloseClipboard()

        # set clipboard to selected clip
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32con.CF_TEXT, self.clips[i-1])
        finally:
            win32clipboard.CloseClipboard()

        # paste
        # h = win32api.GetCurrentThreadId()
        # win32process.AttachThreadInput(self.parent.hwnd_focus, h, True)
        win32api.SendMessage(self.parent.hwnd_focus, win32con.WM_PASTE, 0, 0)
        # win32process.AttachThreadInput(self.parent.hwnd_focus, h, False)
        
        # revert clipboard
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32con.CF_TEXT, self.clipboard_previous)
        finally:
            win32clipboard.CloseClipboard()

        # cleanup
        event.widget.iconify()
        # h = win32api.GetCurrentThreadId()
        # win32process.AttachThreadInput(self.parent.hwnd_focus, h, True)
        # win32gui.SetFocus(self.parent.hwnd_focus)
        # win32process.AttachThreadInput(self.parent.hwnd_focus, h, False)
        # win32process.AttachThreadInput(self.parent.hwnd_foreground, h, True)
        # win32gui.SetFocus(self.parent.hwnd_focus)
        # win32process.AttachThreadInput(self.parent.hwnd_foreground, h, False)
        win32gui.SetForegroundWindow(self.parent.hwnd_focus)
        # win32gui.SetForegroundWindow(self.parent.hwnd_foreground)

    def update_clipboard(self):
        try:
            win32clipboard.OpenClipboard()
            self.clip_buffer = win32clipboard.GetClipboardData(win32con.CF_TEXT)
        finally:
            win32clipboard.CloseClipboard()

        if self.clip_buffer == None:
            self.clip_buffer = ""
        else:
            self.clip_buffer == str(self.clip_buffer)

        if self.clip_buffer in self.clips:
            i = self.clips.index(self.clip_buffer)
            self.clips.insert(0, self.clips.pop(i))
        else:
            self.clips.insert(0, self.clip_buffer)
            self.clips.pop()

        for index, clip in enumerate(self.clips):
            self.parent.update_label(index, clip)

    # def update_clipboard(self):
    #     # This doesn't yet work.
    #     self.msg = wintypes.MSG()

    #     if user32.GetMessageA(byref(self.msg), None, 0, 0) != 0:
    #         if self.msg.message == 797: # WM_CLIPBOARDUPDATE
    #             try:
    #                 win32clipboard.OpenClipboard()
    #                 self.clip_buffer = win32clipboard.GetClipboardData(win32con.CF_TEXT)
    #             finally:
    #                 win32clipboard.CloseClipboard()

    #             if self.clip_buffer == None:
    #                 self.clip_buffer = ""
    #             else:
    #                 self.clip_buffer == str(self.clip_buffer)

    #             if self.clip_buffer in self.clips:
    #                 i = self.clips.index(self.clip_buffer)
    #                 self.clips.insert(0, self.clips.pop(i))
    #             else:
    #                 self.clips.insert(0, self.clip_buffer)
    #                 self.clips.pop()

    #             for index, clip in enumerate(self.clips):
    #                 self.parent.update_label(index, clip)

    #     user32.TranslateMessage(byref(self.msg))
    #     user32.DispatchMessageA(byref(self.msg))


def run():
    '''Main app code.'''
    try:
        root = Window()

        if user32.RegisterHotKey(None, 1, win32con.MOD_WIN, ord("V")) != 0:
            print("--Hotkey registered!")
        else:
            print("--Error registering hotkey.")
        user32.AddClipboardFormatListener(win32api.GetCurrentThreadId())
        root.mainloop()
    finally:
        if user32.UnregisterHotKey(None, 1) != 0:
            print("--Hotkey deregistered!")
        else:
            print("--Error deregistering hotkey.")

if __name__ == "__main__":
    run()
