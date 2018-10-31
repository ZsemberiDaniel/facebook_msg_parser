import json
from PIL import ImageTk, Image as PILImage
from definitions import ROOT_DIR
from os.path import join as join_path
from tkinter import *


emotions = ["love", "happy", "good", "neutral", "bad", "angry", "sad", "animal", "food", "meme", "kinky"]
emotions = list(zip(emotions, map(lambda a: a if a < 10 else chr(a + 55), range(len(emotions)))))

with open(join_path(ROOT_DIR, "img", "data.txt")) as file:
    data = json.loads(file.read())

    data_at = 0
    for d in data:
        if d.get("emotions", None) is not None:
            data_at += 1


def getPhoto(path: str) -> ImageTk.PhotoImage:
    image = PILImage.open(join_path(ROOT_DIR, "img", path))
    return ImageTk.PhotoImage(image)


class Application(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()

        self.out_of_label = Label(self, text="")
        self.out_of_label.pack()

        # emoji image
        self.curr_image = data_at - 1
        self.curr_photo = None
        self.emoji_label = Label(self)
        self._next_image()

        # label
        Label(self, text=" ".join(map(lambda t: "{d[0]}: {d[1]}    ".format(d=t), emotions))).pack()

        # text input
        self.entry = Entry(self)
        self.entry.focus()
        self.entry.pack(fill="x")

        self.entry.bind("<Return>", self.next_button_pressed)

        # button
        next_button = Button(self, text="Next", padx=5, pady=5)
        next_button.bind("<Button-1>", self.next_button_pressed)
        next_button.pack()

        self.mainloop()

    def next_button_pressed(self, event):
        emotion_str: str = self.entry.get()

        if emotion_str is not "":
            try:
                data[self.curr_image]["emotions"] = list(map(lambda i: emotions[int(i, 16)][0], emotion_str))
            except ValueError:
                self.entry.delete(0, 'end')
                return

            self._next_image()
            self.entry.delete(0, 'end')

    def _next_image(self):
        if self.curr_image >= len(data) - 1:
            return

        self.curr_image += 1

        self.curr_photo = getPhoto(data[self.curr_image]["path"])

        self.emoji_label["image"] = self.curr_photo
        self.emoji_label.pack()

        self.out_of_label["text"] = str(self.curr_image + 1) + "/" + str(len(data))
        self.out_of_label.pack()


Application()
with open(join_path(ROOT_DIR, "img", "data.txt"), "w+") as file:
    file.write(json.dumps(data, indent=4))
