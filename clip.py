from tkinter import *
from time import sleep

def run():
    # create window
    root = Tk()
    root.title("Clippy")
    root.iconbitmap("icon2.ico")
    root.geometry("250x210-0+0") # place window in NE (0 pix left, 0 pix down)
    root.resizable(FALSE,FALSE)

    # function defs yo
    def paste():
        p = root.clipboard_get()
        print(p)

    # configure widgets
    # clip_list = Text(root, height=10, state=DISABLED)
    labels_clips = [Label(root, text="BLAH", width=30) for i in range(10)]
    labels_nums = [Label(root, text=str(i+1)[-1]+".") for i in range(10)]

    for i, n, c in zip(range(10), labels_nums, labels_clips):
        n.grid(column=0, row=i, sticky=E, padx=5)
        c.grid(column=1, row=i)
    
    # place widgets
    # clip_list.pack(fill=BOTH)

    # TODO: sort this out
    # # window sizing
    # xy = str(root.winfo_width()) + "x" + str(root.winfo_reqheight())
    # root.geometry(xy + "-0+0")

    # event handlers
    # clip_list.bind("<Enter>", print("entering"))
    # clip_list.bind("<Leave>", print("leaving"))

    # init clipboard system
    clip_buffer = root.clipboard_get()
    # clip_buffer = root.selection_get(selection="CLIPBOARD") # why use this??
    # clips = [clip_buffer, None, None, None, None, None, None, None, None, None]
    # clips_string = ""
    # for i, e in enumerate(clips):
    #     clips_string += "{}.\t{}\n".format(str(i+1), str(e)[:16])
    labels_clips[0].text = clip_buffer

    # clip_list.config(state=NORMAL)
    # clip_list.insert(END, clips_string)
    # clip_list.config(state=DISABLED)

    root.mainloop()

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

if __name__ == '__main__':
    run()








# # how to append to the clipboard
# r.withdraw()
# r.clipboard_clear()
# r.clipboard_append("MESSAGE")
# r.destroy()