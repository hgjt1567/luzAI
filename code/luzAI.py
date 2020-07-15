import struct
import tkinter as tk
from tkinter import font
import time
import cv2
import serial
from PIL import Image, ImageTk
from imageai.Detection import ObjectDetection

showFeed = False

class App:
    def __init__(self, master, portV):
        # initiating Arduino serial port
        if portV:
            try:
                self.arduino = serial.Serial(portV, 9600)
            except (serial.SerialException):
                tk.messagebox.showinfo("Error", "Invalid port.")
        else:
            self.arduino = None

        self.cam = cv2.VideoCapture(1)
        self.lightMode = 0
        self.followMode = True
        self.height = 0
        self.width = 0
        self.xBound = 0
        self.yBound = 0
        self.x = 0
        self.y = 0

        # Initiating object detection model
        self.detector = ObjectDetection()
        self.detector.setModelTypeAsYOLOv3()
        self.detector.setModelPath("yolo.h5")
        self.custom = self.detector.CustomObjects(person=True)
        self.detector.loadModel("faster")

        self.start = 0

        # Creating GUI
        self.master = master
        master.title('Feed')
        self.cFont = font.Font(family='Comic Sans MS', size=15, weight=font.BOLD)
        frame = tk.Frame(master, bg='white')
        frame.pack()

        self.timeLabel = tk.Label(frame, text="FPS: ", fg='white', bg='orange', width=15, height=1)
        self.timeLabel['font'] = self.cFont
        if showFeed:
            self.timeLabel.grid(row=0, column=0)
        else:
            self.timeLabel.grid(row=0, column=1)

        self.lightToggle = tk.Button(frame, text="Light:\nOff", fg='white', bg='orange', height=3, width=15, cursor='arrow',
                              command=self.toggleLight)
        self.lightToggle['font'] = self.cFont
        if showFeed:
            self.lightToggle.grid(row=2, column=0, sticky='W')
        else:
            self.lightToggle.grid(row=1, column=0)

        self.followToggle = tk.Button(frame, text="Following:\nTrue", fg='white', bg='orange', height=3, width=15,
                                     cursor='arrow',
                                     command=self.toggleFollow)
        self.followToggle['font'] = self.cFont
        if showFeed:
            self.followToggle.grid(row=2, column=0)
        else:
            self.followToggle.grid(row=1, column=1)

        self.stop = tk.Button(master=frame, text="Stop", fg='white', bg='orange', height=3, width=15, cursor='arrow',
                              command=self.master.destroy)
        self.stop['font'] = self.cFont
        if showFeed:
            self.stop.grid(row=2, column=0, sticky='E')
        else:
            self.stop.grid(row=1, column=2)

        ret, output = self.cam.read()


        # Set image bounds
        self.height, self.width, channels = output.shape
        self.xBound = self.width/10
        self.yBound = self.height/8

        detPic, det = self.detector.detectCustomObjectsFromImage(custom_objects=self.custom, input_type="array", input_image=output, output_type="array", minimum_percentage_probability=15)

        if showFeed:
            imageN = ImageTk.PhotoImage(image=Image.fromarray(detPic))
            self.imgLabel = tk.Label(frame, image=imageN)
            self.imgLabel.grid(row=1, column=0)

        self.loop()


    # Turn light on and off
    def toggleLight(self):
        if self.lightMode == 0:
            self.lightMode = 1
            self.lightToggle.configure(text="Light:\nOn")
        else:
            self.lightMode = 0
            self.lightToggle.configure(text="Light:\nOff")


    # Turn object detection and following on/off
    def toggleFollow(self):
        self.followMode = not self.followMode
        if self.followMode:
            self.followToggle.configure(text="Following:\nTrue")
        else:
            self.followToggle.configure(text="Following:\nFalse")


    def loop(self):
        self.start = time.time()
        ret, output = self.cam.read()

        # If follow mode is set to on
        if self.followMode:
            # Detect hands
            detPic, det = self.detector.detectCustomObjectsFromImage(custom_objects=self.custom, input_type="array", input_image=output, output_type="array", minimum_percentage_probability=15)

           # If hand is detected
            if len(det)>0:
                #Get location of detected objects
                location = det[0]['box_points']
                self.x = (location[0]+location[2])/2
                self.y = (location[1]+location[3])/2
                if (self.x>(self.width/2+self.xBound)):
                    self.x = 2
                elif (self.x<(self.width/2-self.xBound)):
                    self.x = 0
                else:
                    self.x = 1

                if (self.y>(self.height/2+self.yBound)):
                    self.y = 0
                elif (self.y<(self.height/2-self.yBound)):
                    self.y = 2
                else:
                    self.y = 1
            else:
                self.x = 1
                self.y = 1

            print(str(self.x) + " " + str(self.y) + " " + str(self.lightMode))

            # Send to Arduino over serial
            if self.arduino is not None:
                self.arduino.write(struct.pack('>BBB', self.x, self.y, self.lightMode))
        else:
            # If nothing is detected
            concatted = "1 1 " + str(self.lightMode)

            print(concatted)
            if self.arduino is not None:
                self.arduino.write(struct.pack('>BBB', 1, 1, self.lightMode))

        if showFeed:
            # Display image
            if self.followMode:
                imageN = ImageTk.PhotoImage(image=Image.fromarray(detPic))
            else:
                imageN = ImageTk.PhotoImage(image=Image.fromarray(output))

            self.imgLabel.configure(image=imageN)
            self.imgLabel.image = imageN

            # FPS counter
            self.timeLabel.configure(text="FPS: " + str(1 / (time.time() - self.start))[0:5])
        else:
            if self.followMode:
                self.timeLabel.configure(text="FPS: " + str(1 / (time.time() - self.start))[0:5])
            else:
                self.timeLabel.configure(text="FPS: Very Fast")

        # Loop back to itself
        self.master.after(1, self.loop)


# Toggle feed on/off
def toggleFeed():
    global showFeed, toggleFeed
    showFeed = not showFeed
    if showFeed:
        toggleFeed.configure(text="Video Feed:\nOn")
    else:
        toggleFeed.configure(text="Video Feed:\nOff")


# Begin
def toggleCam():
    global root
    global port
    serial = port.get()
    root.destroy()
    feed = tk.Tk()
    App(feed, serial)
    feed.mainloop()


# Creating main menu GUI
root = tk.Tk(className='luzAI')
root.geometry("570x200")
bFont = font.Font(family='Comic Sans MS', size=15, weight=font.BOLD)

frame = tk.Frame(master=root, width=10, height=10, bg='white')
frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
root.resizable(0, 0)
frame.columnconfigure([0, 2], minsize=300)
frame.rowconfigure([0, 3], minsize=100)

toggleFeed = tk.Button(master=frame, text="Video Feed:\nOff", fg='white', bg='orange', height=3, width=18,
                       cursor='arrow',
                       command=toggleFeed)
toggleFeed['font'] = bFont
toggleFeed.grid(row=0, column=0)

tFont = font.Font(family='Comic Sans MS', size=25, weight=font.BOLD)

label = tk.Label(master=frame, text="Arduino Port:\n(Blank for no Arduino)", height=3, width=24, fg='orange', bg='white', font=bFont)
label.grid(column=0, row=1)

port=tk.Entry(master=frame, width=12, bg='orange', fg='white')
port['font'] = tFont
port.grid(column=1, row=1)

runButton = tk.Button(master=frame, text="Run", fg='white', bg='orange', height=3, width=18, cursor='arrow',
                      command=toggleCam)
runButton['font'] = bFont
runButton.grid(row=0, column=1)

root.mainloop()
