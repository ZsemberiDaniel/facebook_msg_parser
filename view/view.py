from tkinter import *


root = Tk()
root.title("Facebook Messages Analyzer")


class SelectChatFrame(Frame):
    def __init__(self, master=None):
        super().__init__(master=master)
        self.grid(column=0, row=0)

        Label(self, text="Alma").grid()


select_chat = SelectChatFrame(root)
select_chat.grid()

root.mainloop()
