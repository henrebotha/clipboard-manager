# Issues:
# - long clips cause grid elements to stretch - fix this
# - global hotkey needs implementation
# - pasting needs implementation (requires global hotkey first!)
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
        # general init
        self.my_clipboard = Clipboard(self)
        self.clips_vars = [StringVar(i) for i in self.my_clipboard.clips]
        self.labels_clips = [Label(self, textvariable=self.clips_vars[i],
            width=30, anchor=W) for i in range(len(self.my_clipboard.clips))]
        self.labels_nums = [Label(self,
            text=str(i+1)[-1]+".") for i in range(10)]
        # event bindings
        for i in range(10):
            s = "<Key-{}>".format(str(i+1)[-1])
            self.bind_all(s, self.my_clipboard.paste)

        self.place_widgets()

        self.my_clipboard.update_clipboard()

    def place_widgets(self):
        '''Arrange all widgets in the window.'''
        for i, n, c in zip(range(10), self.labels_nums, self.labels_clips):
            n.grid(column=0, row=i, padx=5)
            c.grid(column=1, row=i)

    def update_label(self, index, text):
        '''Change the clip at index to text and update its corresponding label.'''
        self.my_clipboard.clips[index] = text
        self.clips_vars[index].set(text)


class Clipboard(object):
    def __init__(self, parent):
        self.clips = ["" for i in range(10)]
        self.parent = parent

    def paste(self, event):
        i = int(event.keysym)
        if i == 0:
            i = 10
        print(self.clips[i-1])

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
            self.clip_buffer == str(self.clip_buffer)
        if self.clip_buffer in self.clips:
            i = self.clips.index(self.clip_buffer)
            self.clips.insert(0, self.clips.pop(i))
        else:
            self.clips.insert(0, self.clip_buffer)
            self.clips.pop()
        for index, clip in enumerate(self.clips):
            self.parent.update_label(index, clip)
        self.parent.after(1, self.update_clipboard)

# def hotkey_handler(root):
#     try:
#         msg = wintypes.MSG()
#         while user32.GetMessageA(byref(msg), None, 0, 0) != 0:
#             if msg.message == win32con.WM_HOTKEY:
#                 # root.deiconify()
#                 print("hotkey pressed")

#             user32.TranslateMessage(byref(msg))
#             user32.DispatchMessageA(byref(msg))
            
#     finally:
#         user32.UnregisterHotKey(None, 1)

#     # root.deiconify()
#     root.after(1, hotkey_handler, root)

def hotkey_handler(root):
    msg = wintypes.MSG()
    if user32.GetMessageA(byref(msg), None, 0, 0) != 0:
        if msg.message == win32con.WM_HOTKEY:
            if msg.wParam == 1:
                root.deiconify()
    user32.TranslateMessage(byref(msg))
    user32.DispatchMessageA(byref(msg))
    # user32.UnregisterHotKey(None, 1)
    root.after(1, hotkey_handler, root)

def run():
    '''Main app code.'''
    root = Window()

    if user32.RegisterHotKey(None, 1, win32con.MOD_WIN, ord("V")) != 0:
        print("--Hotkey registered!")
    else:
        print("--Error registering hotkey.")

    root.after(1, hotkey_handler, root)

    root.mainloop()

    if user32.UnregisterHotKey(None, 1) != 0:
        print("--Hotkey deregistered!")
    else:
        print("--Error deregistering hotkey.")

if __name__ == "__main__":
    run()


    # from Tkinter import *
    # from time import sleep

    # root = Tk()
    # var = StringVar()
    # var.set('hello')

    # l = Label(root, textvariable = var)
    # l.pack()

    # e = Entry(root)
    # e.pack()
    # e.bind(sequence='<KeyRelease>', func=updatetext)

    # def updatetext(event):
    #     var.set(e.get())
    #     root.update_idletasks() 
