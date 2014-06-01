# Issues:
# - long clips will only show the last part of the clip. Correction will require
#   creating a Clip class that can contain both the full text of a clip, and a
#   display-friendly version
# - pasting needs implementation
# - clipboard detection is broken! it only detects the last-copied item, and
#   only when opening the window.

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
        self.hwnd_mostrecent = None
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
                    # TODO: get handle of currently-focused window text box
                    # self.hwnd_mostrecent = win32gui.GetWindow(win32gui.GetForegroundWindow(), win32con.GW_CHILD) # only works in Notepad
                    # self.hwnd_mostrecent = win32gui.GetFocus()
                    # self.hwnd_mostrecent = user32.GetGUIThreadInfo(win32con.NULL)
                    # print("HWND: " + str(self.hwnd_mostrecent))

                    # self.hwnd_foreground = win32gui.GetForegroundWindow()
                    # self.tid_self = win32process.GetWindowThreadProcessId(None)[0]
                    # self.tid_foreground = win32process.GetWindowThreadProcessId(self.hwnd_foreground)[0]
                    # if self.tid_self != self.tid_foreground:
                    #     win32process.AttachThreadInput(self.tid_self, self.tid_foreground, True)
                    # self.hwnd_focus = win32gui.GetFocus()

                    gui = GUITHREADINFO(cbSize=ctypes.sizeof(GUITHREADINFO))
                    self.hwnd_foreground = win32gui.GetForegroundWindow()
                    # self.tid_foreground = win32process.GetWindowThreadProcessId(self.hwnd_foreground)[0]
                    if user32.GetGUIThreadInfo(0, byref(gui)) == False:
                        print("ERROR #" + str(win32api.GetLastError()))
                    self.hwnd_focus = gui.hwndFocus

                    # END TODO
                    self.after(1, self.update)
                    self.deiconify()
        user32.TranslateMessage(byref(self.msg))
        user32.DispatchMessageA(byref(self.msg))
        # self.after(1, self.hotkey_handler)

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
        # print(self.clips[i-1])

        # store current clipboard state
        win32clipboard.OpenClipboard()
        self.clipboard_previous = win32clipboard.GetClipboardData(win32con.CF_TEXT)
        win32clipboard.CloseClipboard()

        # set clipboard to selected clip
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_TEXT, self.clips[i-1])
        win32clipboard.CloseClipboard()

        # paste
        win32api.SendMessage(self.parent.hwnd_focus, win32con.WM_PASTE, 0, 0)
        
        # revert clipboard
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_TEXT, self.clipboard_previous)
        win32clipboard.CloseClipboard()

        # cleanup
        # if self.parent.tid_foreground != self.parent.tid_self:
        #     win32process.AttachThreadInput(self.parent.tid_self, self.parent.tid_foreground, False)
        event.widget.iconify()
        win32gui.SetForegroundWindow(self.parent.hwnd_foreground)

    def update_clipboard(self):
        win32clipboard.OpenClipboard()
        self.clip_buffer = win32clipboard.GetClipboardData(win32con.CF_TEXT)
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


def run():
    '''Main app code.'''
    try:
        root = Window()

        if user32.RegisterHotKey(None, 1, win32con.MOD_WIN, ord("V")) != 0:
            print("--Hotkey registered!")
        else:
            print("--Error registering hotkey.")

        root.mainloop()
    finally:
        if user32.UnregisterHotKey(None, 1) != 0:
            print("--Hotkey deregistered!")
        else:
            print("--Error deregistering hotkey.")

if __name__ == "__main__":
    run()
