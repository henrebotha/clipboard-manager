from tkinter import *
from time import sleep
import ctypes
from ctypes import wintypes
import win32con

class Window(Tk):
    def __init__(self):
        super().__init__()
        self.title("Clippy")
        self.iconbitmap("icon2.ico")
        self.geometry("250x210-0+0") # place window in NE (0 left, 0 down)
        self.resizable(FALSE,FALSE)
        self.my_clipboard = Clipboard()
        self.clips_vars = [StringVar(i) for i in self.my_clipboard.clips]
        self.labels_clips = [Label(self, textvariable=self.clips_vars[i],
            width=30, anchor=W) for i in range(len(self.my_clipboard.clips))]
        self.labels_nums = [Label(self,
            text=str(i+1)[-1]+".") for i in range(10)]

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
    def __init__(self):
        self.clips = ["" for i in range(10)]


# def hotkey_handler(root):
#     print("hotkey pressed")
#     try:
#         msg = wintypes.MSG()
#         while ctypes.windll.user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
#             if msg.message == win32con.WM_HOTKEY:
#                 root.deiconify()

#             ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
#             ctypes.windll.user32.DispatchMessageA(ctypes.byref(msg))
            
#     finally:
#         ctypes.windll.user32.UnregisterHotKey(None, 1)

#     root.deiconify()
#     root.after(0, hotkey_handler)

# def place_widgets(nums, clips):
#     '''Arrange all widgets in the window.'''
#     for i, n, c in zip(range(10), nums, clips):
#         n.grid(column=0, row=i, padx=5)
#         c.grid(column=1, row=i)

# def make_window():
#     '''Create the window.'''
#     r = Tk()
#     r.title("Clippy")
#     r.iconbitmap("icon2.ico")
#     r.geometry("250x210-0+0") # place window in NE (0 pix left, 0 pix down)
#     r.resizable(FALSE,FALSE)
#     return r

# def update_label(index, text, clips, clips_vars):
#     '''Change the clip at index to text and update its corresponding label.'''
#     clips[index] = text
#     clips_vars[index].set(text)

def run():
    '''Main app code.'''
    root = Window()

    # -------------------------------------------------------------------------
    # TODO: everything below here needs to move to Window or Clipboard class
    # |
    # |
    # |
    
    # configure widgets
    # clipboard
    # clips = ["" for i in range(10)]
    # gui
    # clips_vars = [StringVar(i) for i in clips]
    # labels_clips = [Label(root, textvariable=clips_vars[i], width=30,
    #     anchor=W) for i in range(len(clips))]
    # labels_nums = [Label(root, text=str(i+1)[-1]+".") for i in range(10)]
    
    Window.place_widgets(root) # Why does it want explicit self reference?!

    # event handler definitions
    def paste(event):
        i = int(event.keysym)
        if i == 0:
            i = 10
        print(root.my_clipboard.clips[i-1])
        event.widget.iconify()

    # event handler bindings
    for i in range(10):
        s = "<Key-{}>".format(str(i+1)[-1])
        root.bind_all(s, paste)

    # init clipboard system
    clip_buffer = root.clipboard_get()
    if clip_buffer == None:
        clip_buffer = ""
    # clip_buffer = root.selection_get(selection="CLIPBOARD") # why use this??
    root.update_label(0, clip_buffer)

    # ctypes.windll.user32.RegisterHotKey(None, 1, win32con.MOD_WIN,
    #     win32con.VK_F3)

    # root.after(1, hotkey_handler, root)

    # |
    # |
    # |
    # Window/Clipboard class stuff ends here
    # -------------------------------------------------------------------------

    root.mainloop()

if __name__ == "__main__":
    run()


# TODO: put this inside mainloop using events or w/e
# runtime = 50
# while True:
#     clip = root.selection_get(selection="CLIPBOARD")
#     if clip != clip_buffer:
#         clips.append(clip)
#         clip_buffer = clip
#     print(clips)
#     sleep(0.25)
#     runtime -= 1
#     if runtime < 0:
#         break

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
