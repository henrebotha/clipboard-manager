from tkinter import *
from time import sleep

def run():
    # create window
    root = Tk()
    root.title("Clippy")
    root.iconbitmap("icon2.ico")
    root.geometry("250x195-0+0") # place window in NE (0 pix left, 0 pix down)
    root.resizable(FALSE,FALSE)

    # function defs yo
    def paste():
        p = root.clipboard_get()
        print(p)

    # widgets
    clip_list = Text(root, height=10)
    clip_list.pack()
    button = Button(root, text="Paste", command=paste)
    button.pack()

    # TODO: sort this out
    # # window sizing
    # xy = str(root.winfo_reqwidth()) + "x" + str(root.winfo_reqheight())
    # root.geometry(xy + "-0+0")

    # event handlers
    clip_list.bind("<Enter>", print("entering"))
    clip_list.bind("<Leave>", print("leaving"))

    # init clipboard system
    clip_buffer = root.clipboard_get()
    # clip_buffer = root.selection_get(selection="CLIPBOARD") # why use this??
    clips = [clip_buffer]
    runtime = 50

    root.mainloop()

    # TODO: put this inside mainloop using events or w/e
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

if __name__ == '__main__':
    run()








# # how to append to the clipboard
# r.withdraw()
# r.clipboard_clear()
# r.clipboard_append("MESSAGE")
# r.destroy()