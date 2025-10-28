#manage staff page

#import here
import tkinter as tk
from add_staff import AddStaffPage
from PIL import Image, ImageTk

class ManageStaffPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(bg="white", padx=150, pady=40)
        
        image = Image.open("img12.png") 
        image = image.resize((800, 600))  
        self.photo = ImageTk.PhotoImage(image)  
        image_label = tk.Label(self, image=self.photo, bg="white")
        image_label.grid(row=0, column=0, rowspan=15, padx=80, pady=80) 

        #frontend
        tk.Label(self, text="Manage Staff",fg="#cc0000" ,bg="white",font=("Arial", 20)).grid(row=0, column=1, pady=(60, 30))

        tk.Button(self, text="Add a New Staff Member", font=("Arial", 14), command=lambda: self.app.show_page(AddStaffPage)).grid(row=1, column=1, sticky="w", padx=10)
        
        #import here to avoid circular import error
        from main_menu import MainMenuPage
        tk.Button(self, text="Back", font=("Arial", 14), command=lambda: self.app.show_page(MainMenuPage)).grid(row=2, column=1, sticky="w", padx=10)
