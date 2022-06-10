import Tkinter as tk
from PIL import ImageTk, Image
import tkFileDialog as filedialog
import cv2 as cv
import imutils

cap = None
root = tk.Tk()
root.title('MrMime2')
root.geometry('1000x1000')
root.resizable(0,0)
#root.iconbitmap('image.jpg')

def visualizar():
    global cap
    if cap is not None:
        ret, frame = cap.read()
        if ret == True:
            frame = imutils.resize(frame, width=640)
            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            im = Image.fromarray(frame)
            img = ImageTk.PhotoImage(image=im)
            lblVideo.configure(image=img)
            lblVideo.image = img
            lblVideo.after(10, visualizar)
        else:
            lblVideo.image = ""
            cap.release()

def iniciar():
    global cap
    cap = cv.VideoCapture(0)
    visualizar()

def open():
    global my_image
    root.filename = filedialog.askopenfilename(initialdir="/Documentos/GitHub/MrMime2", title="Select a File", filetypes=(("jpg files", "*.jpg"),("png files", "*.png")))
    my_label = tk.Label(root, text=root.filename)
    my_label.pack()
    my_image = ImageTk.PhotoImage(Image.open(root.filename))
    my_image_label = tk.Label(image=my_image)
    my_image_label.pack()

my_btn = tk.Button(root, text = "Open File", command = open).pack()
my_btn2 = tk.Button(root, text = "Video", command = iniciar).pack()
lblVideo = tk.Label(root)
lblVideo.pack()
root.mainloop()