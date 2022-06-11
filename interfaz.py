import Tkinter as tk
from PIL import ImageTk, Image
import tkFileDialog as filedialog
import cv2 as cv
import imutils


cap = None
root = tk.Tk()
root.title('MrMime2')
root.geometry('960x540') #SD
root.config(bg='#C19BA6')
root.resizable(0,0)
#root.iconbitmap('image.jpg')

def visualizar():
    global cap
    if cap is not None:
        ret, frame = cap.read()
        if ret == True:
            frame = imutils.resize(frame, width=320)
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
    my_label.destroy()
    my_image_label.destroy()
    btn_hpe.destroy()
    visualizar()

def hpe ():
    global my_image2, my_image_label2
    root.filename = filedialog.askopenfilename(initialdir="/Documentos/GitHub/MrMime2", title="Select a File", filetypes=(("jpg files", "*.jpg"),("png files", "*.png")))
    my_image2 = ImageTk.PhotoImage(Image.open(root.filename).resize((200, 200)))
    my_image_label2 = tk.Label(image=my_image2)
    my_image_label2.place(x=380, y=200)

def open():
    global my_image, my_image_label, my_label, btn_hpe
    root.filename = filedialog.askopenfilename(initialdir="/Documentos/GitHub/MrMime2", title="Select a File", filetypes=(("jpg files", "*.jpg"),("png files", "*.png")))
    my_label = tk.Label(root, text="Ruta de la imagen: \n\n" + root.filename, fg="black", bg="white", font='Helvetica 10 bold')
    my_label.place(x=0, y=25)
    my_image = ImageTk.PhotoImage(Image.open(root.filename).resize((200, 200)))
    my_image_label = tk.Label(image=my_image)
    my_image_label.place(x=80, y=100)
    btn_hpe = tk.Button(root, text = "Activar HPE", command = hpe, fg="black", bg="white", font="Helvetica 10 bold")
    btn_hpe.config(height=3, width = 20)
    btn_hpe.place(x=400, y=100)


my_btn = tk.Button(root, text = "Cargar Archivo", command = open, fg="black", bg="white", font="Helvetica 10 bold")
my_btn.config(height=3,width=20)
my_btn.place(x= 400, y=20)
my_btn2 = tk.Button(root, text = "Usar Camara", command = iniciar, fg="black", bg="white", font="Helvetica 10 bold")
my_btn2.config(height=3, width=20)
my_btn2.place(x=720, y = 20)

lblVideo = tk.Label(root)
lblVideo.place(x=80, y=120)
root.mainloop()