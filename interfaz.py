from tkinter import *
from PIL import ImageTk, Image
from tkinter import filedialog

root = Tk()
root.title('MrMime2')
root.iconbitmap('image.jpg')

def open():
    global my_image
    root.filename = filedialog.askopenfilename(initialdir="/Documentos/GitHub/MrMime2", title="Select a File", filetypes=(("jpg files", "*.jpg"),("png files", "*.png")))
    my_label = Label(root, text=root.filename).pack()
    my_image = ImageTk.PhotoImage(Image.open(root.filename))
    my_image_label = Label(image=my_image).pack()

my_btn = Button(root, text = "Open File", command = open).pack()
root.mainloop()