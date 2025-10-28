#login page

#import here
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from models import Staff
from main_menu import MainMenuPage
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

#inherits from App class in app.py
class LoginPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(bg="white", padx=130, pady=40)
        
        image = Image.open("img9.jpg") 
        image = image.resize((800, 600))  
        self.photo = ImageTk.PhotoImage(image)  
        image_label = tk.Label(self, image=self.photo, bg="white")
        image_label.grid(row=0, column=0, rowspan=15, padx=80, pady=80)  

        # Login title
        tk.Label(self, text="Login", font=("Arial", 18, "bold"), bg="white").grid(row=0, column=1, pady=(60, 30))

        # Email field
        tk.Label(self, text="Email:", font=("Arial", 14), bg="white").grid(row=1, column=1, sticky="w", padx=10)
        self.email_entry = tk.Entry(self, font=("Arial", 14), width=25, relief="solid", bd=1)
        self.email_entry.grid(row=2, column=1, padx=10, pady=5)

        # Password field
        tk.Label(self, text="Password:", font=("Arial", 14), bg="white").grid(row=3, column=1, sticky="w", padx=10)
        self.password_entry = tk.Entry(self, show="*", font=("Arial", 14), width=25, relief="solid", bd=1)
        self.password_entry.grid(row=4, column=1, padx=10, pady=5)

        # Login button
        tk.Button(self, text="Login", font=("Arial", 14, "bold"), command=self.login, 
                  bg="#1E90FF", fg="white", relief="flat", width=20).grid(row=5, column=1, pady=20)

    #runs when login button is pressed
    def login(self):
        #get email and password entered by user .strip() = remove leading/trailing whitespace to avoid issues in validation
        email = self.email_entry.get().strip()
        password = self.password_entry.get() #don't strip password as passwords must be handled exactly as entered

        #if no email and/or password has been entered return an error message
        if not email or not password:
            messagebox.showerror("Error", "Please enter both email and password.")
            return

        #query the database with the email given
        staff_member = self.app.session.query(Staff).filter_by(email=email).first()

        #if the email exists check if the password matches
        if staff_member:
            try:
                #if the email exists and the associated password matches, navigate to the main menu
                if ph.verify(staff_member.password, password):
                    #set the user attribute (initialised in app.py) to the logged in staff member (so details can be accessed centrally)
                    self.app.user = staff_member
                    self.app.show_page(MainMenuPage)
            except VerifyMismatchError:
                #otherwise return an error message
                messagebox.showerror("Error", "Incorrect email or password.")
        #otherwise return an error message
        else:
            messagebox.showerror("Error", "Incorrect email or password.")
