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

                    self.hwnd_foreground = win32gui.GetForegroundWindow()
                    # print("hwnd_foreground: " + str(self.hwnd_foreground))
                    # _, self.pid_self = win32process.GetWindowThreadProcessId(None)
                    self.pid_self = win32api.GetCurrentThreadId()
                    # print("pid_self: " + str(self.pid_self))
                    self.pid_foreground = win32process.GetWindowThreadProcessId(self.hwnd_foreground)[0]
                    # print("pid_foreground: " + str(self.pid_foreground))
                    if self.pid_self != self.pid_foreground:
                        win32process.AttachThreadInput(self.pid_foreground, self.pid_self, True)
                    self.hwnd_focus = win32gui.GetFocus()
                    # print("hwnd_focus: " + str(self.hwnd_focus))
                    # win32process.AttachThreadInput(self.pid_foreground, self.pid_self, False)

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

        # Implementation:
        # - on global hotkey press, find handle to current window before
        #   deiconifying this window
        # - on paste, send WM_PASTE message to said window
        # Important: it's not possible to WM_PASTE a given string, so we need to
        # store the current state of the clipboard, change it to what we want to
        # paste, WM_PASTE, then revert the clipboard

        # # http://bytes.com/topic/python/answers/646943-get-control-over-window
        # hwnd = user32.FindWindowA(None, "Notepad") # obviously wrong
        # win32api.SendMessage(hwnd, win32con.WM_PASTE, 0, 0)
        # # http://bytes.com/topic/python/answers/646943-get-control-over-window

        # seems to be working, so far

        # store current clipboard state
        self.clipboard_previous = win32clipboard.GetClipboardData(win32con.CF_TEXT)

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
        if self.parent.pid_foreground != self.parent.pid_self:
            win32process.AttachThreadInput(self.parent.pid_foreground, self.parent.pid_self, False)
        event.widget.iconify()
        win32gui.SetForegroundWindow(self.parent.hwnd_foreground)

    def update_clipboard(self):
        self.clip_buffer = win32clipboard.GetClipboardData(win32con.CF_TEXT)
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
