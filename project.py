import cv2
import numpy as np
import tkinter
from tkinter import filedialog
import math
#Function to parse index to gender string
def getGender(x):
    if x==0:
        return "Male"
    elif x==1:
        return "Female"
    else:
        return "Error"
#Function to parse index to semester string
def getSemester(x):
    if x==0:
        return "Fall"
    elif x==1:
        return "Spring"
    elif x==2:
        return "Summer"
    else:
        return "Error"
#Function to parse index to program string
def getProgram(x):
    if x==0:
        return "MCTA"
    elif x==1:
        return "ENVER"
    elif x==2:
        return "BLDG"
    elif x==3:
        return "CESS"
    elif x==4:
        return "ERGY"
    elif x==5:
        return "COMM"
    elif x==6:
        return "MANF"
    elif x==7:
        return "LAAR"
    elif x==8:
        return "MATL"
    elif x==9:
        return "CISE"
    elif x==10:
        return "HAUD"
    else:
        return "ERROR"
#Function to parse index to answer string
def getAnswer(x):
    if x==0:
        return "STRONGLY AGREE"
    elif x==1:
        return "AGREE"
    elif x==2:
        return "NEUTRAL"
    elif x==3:
        return "DISAGREE"
    elif x==4:
        return "STRONGLY DISAGREE"
    else:
        return "ERROR"
#initialising tkinter
root = tkinter.Tk()
root.withdraw()
#Opening file window to select input image
filepath=filedialog.askopenfilename()
#opening creating and opening output.txt file
file=open("output.txt","w+")
#opening original image
original=cv2.imread(filepath,1)
#applying median blur to image
sample=cv2.medianBlur(original,5)
#converting image to grayscale
sample=cv2.cvtColor(sample,cv2.COLOR_BGR2GRAY)
#cropping image to get a partition which will be used to correct the image's orientation
lined=original[100:500,0:1900]
#canny edge detector is applied
edges = cv2.Canny(lined,50,150,apertureSize = 3)
#Hough line detector is used to get the lines
lines = cv2.HoughLines(edges,1,np.pi/180,200)
#theta of the first line is used
for rho,theta in lines[0]:
    #Theta is converted from radians to degrees
    inDeg=theta*180/np.pi
    print(inDeg)
    #if theta is 90 degrees then the line is perfectly horizontal and the image is correctly oriented
    if math.floor(inDeg)!=90:
        #If it is not 90 degrees then the difference is used to rotate the image using affine
        (h, w) = sample.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, inDeg-90, 1.0)
        rotated = cv2.warpAffine(sample, M, (w, h),
                                 flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        sample=rotated

#hough circles is used to get the circles in the image
circ=cv2.HoughCircles(sample,cv2.HOUGH_GRADIENT,1,20,param1=50,param2=30,minRadius=5,maxRadius=20)
circles = np.uint16(np.around(circ))
#circles are drawn in black on the image
for i in circles[0,:]:
    cv2.circle(sample,(i[0],i[1]),i[2],(0,255,0),2)
#a threshold is used to make the image binary with only the circles visible
x,sample=cv2.threshold(sample,50,255,cv2.THRESH_BINARY)
#the image is inverted to make the circles white and the background black
sample=~sample
#the relevent parts of the image are cropped
gender=sample[250:350,0:1900]
sem=sample[350:400,0:1900]
prog=sample[400:530,0:1900]
q=[]
for i in range(19):
    if i<5:
        q.append(sample[960+(i*40):1000+(i*40),1000:])
    elif i<11:
        q.append(sample[1240 + ((i-5) * 40):1280 + ((i-5) * 40), 1000:])
    elif i<14:
        q.append(sample[1560 + ((i - 11) * 40):1600 + ((i - 11) * 40), 1000:])
    elif i<16:
        q.append(sample[1760 + ((i - 14) * 40):1800 + ((i - 14) * 40), 1000:])
    elif i<17:
        q.append(sample[1880 + ((i - 16) * 40):1920 + ((i - 16) * 40), 1000:])
    elif i<19:
        q.append(sample[2000 + ((i - 17) * 40):2040 + ((i - 17) * 40), 1000:])
#the previously cropped images are cropped again to make sure each image has a pixel on the first row of the image to correct their order when they are detected
gender=gender[50:90,0:1900]
#connected components with stats is used to get the choices with their areas
x,y,genderArea,gender2=cv2.connectedComponentsWithStats(gender)
areas=[]
#areas are added to a list
for i in range(1,3):
    areas.append(genderArea[i][4])
print(getGender(areas.index(max(areas))))
#the index of the max area is parsed to its corresponding string then written to the file
file.write("Gender: "+getGender(areas.index(max(areas)))+"\r\n")
#the same sequence is done to the semester
sem=sem[25:,0:1900]
x,y,semArea,gender2=cv2.connectedComponentsWithStats(sem)
sems=[]
for i in range(1,4):
    sems.append(semArea[i][4])
print(getSemester(sems.index(max(sems))))
file.write("Semester: "+getSemester(sems.index(max(sems)))+"\r\n")
#the same is done to the program except that it is cropped to two images due to its options being on 2 rows and to preserce their order
prog1=prog[50:80,0:1900]
prog2=prog[90:120,0:1900]
a,b,progA1,c=cv2.connectedComponentsWithStats(prog1)
a2,b,progA2,c=cv2.connectedComponentsWithStats(prog2)
progs=[]
for i in range(1,8):
    progs.append(progA1[i][4])
for i in range(1,5):
    progs.append(progA2[i][4])
print(getProgram(progs.index(max(progs))))
file.write("Program: "+getProgram(progs.index(max(progs)))+"\r\n")
questions=[]
#the same is done to the questions
for i in range(19):
    questions.append([])
    q[i]=q[i][10:40,0:1920]
    a,b,quesA,c=cv2.connectedComponentsWithStats(q[i])
    for j in range(1,6):
        questions[i].append(quesA[j][4])
    print(getAnswer(questions[i].index(max(questions[i]))))
    file.write(getAnswer(questions[i].index(max(questions[i])))+"\r\n")
file.close()
cv2.waitKey()