import qrcode
import json
import sqlite3
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, Frame
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch,mm
import tkinter as tk
from reportlab.pdfgen import canvas
from PIL import Image, ImageTk
from tkinter import ttk
from tkinter import filedialog,messagebox
import os
import sys
import tempfile

#student class function where will contain functions for validating and adding student
class Student:
    def __init__(self,student):
        self.name=student["Name"]
        self.number=student["Number"]
        self.gender=student["Gender"]
        self.course=student["Course"]
        self.passport=student["Photo"]
        self.data={
            "Name":self.name,
            "Registration Number":self.number,
            "Gender":self.gender,
            "Course":self.course
        }
        self.confirm()
#adds details to database    
    def add_name(self):
        
        Database().add()

#generate card
    def generate_card(self):
        Build_qr(self.data)             

#confirm if student exists
    def confirm(self):
        value=Database().confirm_data(self.number)
        if not value:
            self.generate_card()



#The generate card class that handles generating of student exam cards
class Generate_card:
    def __init__(self,qr_data):
        self.qr_data=qr_data
        self.data=json.loads(self.qr_data["qr_data"])
        self.generate()
    def generate(self):
        print("Generate card")
        width=3.37*inch
        height=2.125*inch
        margin = 0.1 * inch
        size=(width,height)
        filename=self.data['Name'].strip().replace(" ","_")
        c=canvas.Canvas(f"{filename} exam_card.pdf",pagesize=size)
        header_height=0.6*inch
#This tells canvas from now on , if I draw a filled shape use this color to fill it     
        c.setFillColor(colors.HexColor("#0C2D17"))
        c.rect(0, height-header_height, width, header_height, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(width/2, height-20, "Dedan Kimathi University of Technology")
        c.setFont("Helvetica-Oblique", 7)
        c.drawCentredString(width/2, height-32, "Better Life through Technology")
        c.setFont("Helvetica", 6)
        c.setFillColor(colors.black)
        c.drawRightString(
        width - 5,
        height - (header_height + 10),
        "SEP-DEC 2025"
        )
        tempfile_path=None
        try:
            fd, tempfile_path = tempfile.mkstemp(suffix=".png")
            os.close(fd)
            self.qr_data["qr_image"].save(tempfile_path,format="PNG")
            qr_code_image=tempfile_path
            c.drawImage(
            qr_code_image,
            10,
            height - 120,
            width=60,
            height=60
            )
        finally:
            if tempfile_path and os.path.exists(tempfile_path):
                os.remove(tempfile_path)    
        margin_x=80
        margin_y=height - 75
        c.drawString(margin_x, margin_y, f"Name: {self.data['Name']}")
        c.drawString(margin_x, margin_y - 10, f"Reg No: {self.data['Registration Number']}")
        c.drawString(margin_x, margin_y - 20, f"Gender: {self.data['Gender']}")
        c.drawString(margin_x, margin_y - 30, f"Course: {self.data['Course']}")
        c.setFont("Helvetica", 6)

        c.drawString(
            10,
            10,
            "Downloaded on Friday, January 30, 2026, 08:33:43 PM"
        )

        c.drawRightString(
            width - 5,
            10,
            "Card No # 19361"
        )
        c.save()





#The qr builder that builds the qr code
class Build_qr:
    def __init__(self,data):
        try:
            json_string=json.dumps(data)
            qr=qrcode.QRCode(
            version=1,                # size
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,               # pixel size
            border=4                   # quiet zone
            )

            qr.add_data(json_string)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            #img.save(f"{data['Name']}qr.png")
            Generate_card({"qr_image":img,"qr_data":json_string})
        except json.JSONDecodeError:
            print("Error: The scanned data was not valid JSON.")
        except Exception as e:
            print(f"An error occurred during parsing:{e} ") 


#handles all database logic    
class Database():
    def __init__(self):
        pass
        
#This confirms if the student exists in database as in their name was written there because their exam card was printed        
    def confirm_data(self,number):
        try:    
            with sqlite3.connect("student_data.db") as conn:
                cursor=conn.cursor()
                sqlite_command='''
                SELECT 1 from students WHERE REG_NUMBER=?  
                '''
                cursor.execute(sqlite_command,(number,))
                result=cursor.fetchone()
                
                if result:
                    return True
                else:
                    return False 
        except sqlite3.Error as e:  
            print("Database error occurred: {e}")
            return False         
    def add(self,student):
        self.name=student["Name"]    
        self.number=student["Number"]
        self.gender=student["Gender"]
        self.course=student["Course"]
        try:    
            with sqlite3.connect("student_data.db") as conn:
                cursor=conn.cursor()        
                sqlite_add='''
                INSERT OR IGNORE INTO students(
                    NAME,
                    REG_NUMBER,
                    GENDER,
                    COURSE
                )
                VALUES(?,?,?,?)
                '''
                cursor.execute(sqlite_add,(self.name,self.number,self.gender,self.course))
        except sqlite3.Error as e:  
            print("Database error occurred: {e}")

#Create UI that takes user name,registration number and gender
class BuildGui:
    def __init__(self):
        self.image_thumbnail=None
        self.bg_image=None
        self.reg=None
        self.name=None
        self.course=None
        self.gender=None
        self.reg_entry=None
        self.name_entry=None
        self.gender_choice=None
        self.course_choice=None
        window=tk.Tk()
        window.title("Student Exam card Generator")
        screen_width=window.winfo_screenwidth()
        screen_height=window.winfo_screenheight()
        try:
            self.bg_image=Image.open("Dark.jpg")
            self.bg_image=self.bg_image.resize((screen_width,screen_height),Image.LANCZOS)
            self.bg_image=ImageTk.PhotoImage(self.bg_image)
            bg_label=tk.Label(window,image=self.bg_image)
            bg_label.place(x=0,y=0,relwidth=1,relheight=1)
        except Exception as e:
            print("Error loading background image:", e)
            self.bg_image=None
            window.config(bg="skyblue")#fallback background color
        window.geometry(f"{screen_width}x{screen_height}+0+0")
        main_frame=tk.Frame(window,bg="white",bd=5,relief=tk.RAISED,padx=20,pady=20)
        card_height=int(screen_height*0.7)
        card_width=int(screen_width*0.6)
        main_frame.place(relx=0.5,rely=0.5,anchor="center",width=card_width,height=card_height)    
        last_frame=tk.Frame(main_frame,bg=main_frame.cget("bg"))
        submission_button=tk.Button(last_frame,text="Generate exam card",command=self.get_user_input)
        last_frame.pack(side=tk.BOTTOM,pady=(0,10),fill=tk.X)
        submission_button.pack(side=tk.BOTTOM,pady=(0,10),fill=None)
        BuildGui.bottom_frame(self,main_frame)
        BuildGui.top_frame(self,main_frame)
        BuildGui.middle_frame(self,main_frame)
    
        window.mainloop()


#This builds the top most frame with title and fields for name and registration number with their labels     
    def top_frame(self,main_frame):
        top_frame=tk.Frame(main_frame,bg="#ffffff")
        title_label=tk.Label(top_frame,text="Student Exam Card Generator",font=("Helvetica",14),bg=top_frame.cget("bg"))
        name_label=tk.Label(top_frame,text="Enter your name:",font=("Helvetica",14),bg=top_frame.cget("bg"))
        self.name_entry=tk.Entry(top_frame,font=("Helvetica",14))
        reg_label=tk.Label(top_frame,text="Enter reg no:",font=("Helvetica",14),bg=top_frame.cget("bg"))
        self.reg_entry=tk.Entry(top_frame,font=("Helvetica",14))
        top_frame.pack(side=tk.TOP,pady=(0,10),fill=tk.X)
        title_label.grid(row=0,column=1,sticky="ew")
        name_label.grid(row=1,column=0,sticky="w")
        reg_label.grid(row=1,column=2,sticky="e")
        self.name_entry.grid(row=2,column=0,sticky="w")
        self.reg_entry.grid(row=2,column=2,sticky="e")

#This builds the middle frame with upload functionality
    def middle_frame(self,main_frame):
        middle_frame=tk.Frame(main_frame,bg="#ffffff")
        heading_label=tk.Label(middle_frame,text="Select your passport photo",font=("Helvetica",14),bg=middle_frame.cget("bg"))
        display_image=tk.Label(middle_frame,bg=middle_frame.cget("bg"))
        #1️⃣Allow the user to pick a file in the computer
        
        def select_file():
            file_path=filedialog.askopenfilename(title="Select any file",filetypes=[("All files", "*.*")])
            nonlocal display_image
            if file_path:
                print(f"Selected file: {file_path}")
                PASSPORT_PHOTO_REQUIREMENTS = {
            "min_width":600,
            "min_height":600,
            "max_height":1200,
            "max_width":1200,
            "aspect_ratio":1.0,
            "aspect_ratio_tolerance":0.01,
            "max_file_size":5,
            "allowed_formats":['JPEG','PNG']
            }
            try:
            #2️⃣Access file info picked by user for validation 
            #3️⃣Validate it's a photo   
                image=Image.open(file_path)
                image_format=image.format
                image_size_tuple=image.size
            
            #4️⃣Validate it's passport size
                message_errors=[]
                is_valid=True
                if not (image_size_tuple[0]>=PASSPORT_PHOTO_REQUIREMENTS["min_width"] and image_size_tuple[0]<=PASSPORT_PHOTO_REQUIREMENTS["max_width"]):
                    is_valid=False
                    message_errors.append(f"Image  width is not within required range {PASSPORT_PHOTO_REQUIREMENTS['min_width']}-{PASSPORT_PHOTO_REQUIREMENTS['max_width']}px).")
                if not(image_size_tuple[1]>=PASSPORT_PHOTO_REQUIREMENTS["min_height"] and image_size_tuple[1]<=PASSPORT_PHOTO_REQUIREMENTS["max_height"]):
                    is_valid=False
                    message_errors.append(f"Image  height is not within required range {PASSPORT_PHOTO_REQUIREMENTS['min_height']}-{PASSPORT_PHOTO_REQUIREMENTS['max_height']}px).")
                if image_size_tuple[1]==0:
                    is_valid=False
                    message_errors.append("Image height is zero, cannot calculate aspect ratio.")
                else:        
                    image_ratio=image_size_tuple[0]/image_size_tuple[1]
                    if not(image_ratio<=(PASSPORT_PHOTO_REQUIREMENTS["aspect_ratio"]+PASSPORT_PHOTO_REQUIREMENTS["aspect_ratio_tolerance"]) and image_ratio>=(PASSPORT_PHOTO_REQUIREMENTS["aspect_ratio"]-PASSPORT_PHOTO_REQUIREMENTS["aspect_ratio_tolerance"])):         
                        is_valid=False
                        message_errors.append(f"Aspect ratio ({image_ratio:.2f}) is not 1:1 (square) within  tolerance.")
                if is_valid:                 
                    image.thumbnail((150,100))
                    self.image_thumbnail=ImageTk.PhotoImage(image)
                    display_image.config(image=self.image_thumbnail)
                else:
                #.join() joins for every string join one of it    
                    messagebox.showerror("Validation Failed", "The selected photo does NOT meet requirements:\n"+ "\n" .join(message_errors))    
            #5️⃣Give user feedback success or failure 
            except Image.UnidentifiedImageError:
                messagebox.showerror("Image Format error", f"The file {os.path.basename(file_path)} is not a recognized image format")
            except FileNotFoundError:
                messagebox.showerror("File not found error",f"The file {os.path.basename(file_path)} could not  be found")       
            except Exception as e:
                messagebox.showerror("Unexpected error",f"An unexpected error occurred:{e}")
        
    
            else:
                print("No file selected")
            
        select_button=tk.Button(middle_frame,text="Click to select File",command=select_file)            
        middle_frame.pack(side=tk.TOP,pady=(0,5),fill=tk.BOTH,expand=True)
        heading_label.grid(row=0,column=2,sticky="ew",padx=(200,0))
        display_image.grid(row=1,column=2,sticky="nsew",padx=(200,0),pady=(20,30))
        select_button.grid(row=2,column=2,sticky="ew",padx=(200,0))

#This builds the bottom frame with course and gender fields to fill    
    def bottom_frame(self,main_frame):
        bottom_frame=tk.Frame(main_frame,bg="#ffffff")          
        courses=["Mechatronics Engineering","Computer Science","IT","Mechanical Engineering","Electrical Engineering","Telecommunications Engineering","Leather Tanning technology"]
        genders=["Male","Female"]
        course_label=tk.Label(bottom_frame,text="Choose Course:",font=("Helvetica",14),bg=bottom_frame.cget("bg"))
        gender_label=tk.Label(bottom_frame,text="Chose Gender:",font=("Helvetica",14),bg=bottom_frame.cget("bg"))
        self.gender_choice=tk.StringVar()
        self.course_choice=tk.StringVar()
        course_selection=ttk.OptionMenu(bottom_frame,self.course_choice,courses[0],*courses)
        gender_selection=ttk.OptionMenu(bottom_frame,self.gender_choice,genders[0],*genders)
        bottom_frame.pack(side=tk.BOTTOM,pady=(10,0),fill=tk.X,expand=True)
        course_label.grid(row=0,column=0,sticky="w")
        gender_label.grid(row=0,column=2,padx=(200,0),sticky="e")
        course_selection.grid(row=1,column=0,sticky="w")
        gender_selection.grid(row=1,column=2,padx=(200,0),sticky="e")
    def get_user_input(self):
        self.name=self.name_entry.get()
        self.reg=self.reg_entry.get()
        self.gender=self.gender_choice.get()
        self.course=self.course_choice.get()
        student={
        "Name":self.name,
        "Number":self.reg,
        "Gender":self.gender,
        "Course":self.course,
        "Photo":self.image_thumbnail
        }
        Student(student)

#Take that data and confirm if the registration number is identical to database
def main(student):
    number=student["number"]
    if Student.confirm(number):
        Student.generate_card(student)

BuildGui()