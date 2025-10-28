#view listings page

#import here
import tkinter as tk
from tkinter import ttk, messagebox
from models import Cinema, Staff, Role
from utils import is_valid_name, is_valid_email, is_valid_password
from argon2 import PasswordHasher
from PIL import Image, ImageTk

ph = PasswordHasher()

class AddStaffPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.user = self.app.user
        self.configure(bg="white", padx=80, pady=85)
        self.pack(fill="both", expand=True)
        
        # Open the image and resize it
        image = Image.open("img7.jpg")
        image = image.resize((750, 600))

        # Convert image to Tkinter-compatible format
        self.photo = ImageTk.PhotoImage(image)

        # Create a label with the image
        image_label = tk.Label(self, image=self.photo)

        # Use .pack() to place the image on the right side
        image_label.pack(side="right",anchor="ne", padx=130, pady=10)

        #frontend
        tk.Label(self, text="Add a Staff Member", font=("Arial", 30, "bold")).pack(anchor="nw",padx=120,pady=20)

        #add staff form
        tk.Label(self, text="Full Name:", font=("Arial", 18)).pack(padx=50,pady=10)
        self.name_entry = tk.Entry(self, font=("Arial", 18), width=25, relief="solid", bd=1)
        self.name_entry.pack(pady=15)

        tk.Label(self, text="Email:", font=("Arial", 18)).pack(padx=50,pady=10)
        self.email_entry = tk.Entry(self, font=("Arial", 18), width=25, relief="solid", bd=1)
        self.email_entry.pack(pady=15)

        tk.Label(self, text="Password:", font=("Arial", 18)).pack(padx=50,pady=10)
        self.password_entry1 = tk.Entry(self, show="*", font=("Arial", 18), width=25, relief="solid", bd=1)
        self.password_entry1.pack(pady=15)

        tk.Label(self, text="Password Confirmation:", font=("Arial", 18)).pack(padx=50,pady=10)
        self.password_entry2 = tk.Entry(self, show="*", font=("Arial", 18), width=25, relief="solid", bd=1)
        self.password_entry2.pack(pady=15)

        tk.Label(self, text="Role:", font=("Arial", 14)).pack(side="left",padx=10, pady=10)
        user_role = self.user.role.title
        #if the user is manager they can add admins and booking staff otherwise they (admin) can only add booking staff
        if user_role.lower() == "manager":
            role_options = ["Booking Staff", "Admin"]
            #manager can add staff to any cinema
            cinema_query = self.app.session.query(Cinema).all()
        else:
            role_options = ["Booking Staff"]
            #admin can add staff to only the cinema admin works at
            cinema_query = self.app.session.query(Cinema).filter(Cinema.cinema_id == self.user.cinema_id).all()
            
        self.role_dropdown = ttk.Combobox(self, values=role_options, state="readonly")
        self.role_dropdown.pack(side="left",padx=10,pady=10)

        #dict of cinema options with keys as the cinema name and values as the cinema id
        self.cinema_map = {f"HC {cinema.neighbourhood} {cinema.city.name}": cinema.cinema_id for cinema in cinema_query}
        #set dropdown options to the cinema names
        cinema_options = list(self.cinema_map.keys())

        tk.Label(self, text="Cinema:", font=("Arial", 14)).pack(side="left",padx=10,pady=10)
        self.cinema_dropdown = ttk.Combobox(self, values=cinema_options, state="readonly")
        self.cinema_dropdown.pack(side="left",padx=10, pady=10)
        
        tk.Button(self, text="Add Staff", font=("Arial", 14), command=self.add_staff).pack(side="left", padx=10,pady=10)
        
        #import here to avoid circular import error
        from manage_staff import ManageStaffPage
        tk.Button(self, text="Back", font=("Arial", 14), command=lambda: self.app.show_page(ManageStaffPage)).pack(side="left",padx=10,pady=10)


    def add_staff(self):
        #get values entered
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        password1 = self.password_entry1.get() #keep password as entered - don't strip
        password2 = self.password_entry2.get()
        role = self.role_dropdown.get().strip()
        cinema = self.cinema_dropdown.get().strip()

        #validation
        #if one of the details is missing then return error message
        if not name or not email or not password1 or not password2 or not role or not cinema:
            messagebox.showerror("Error", "Please enter all details")
            return

        #name validation
        name_error = is_valid_name("Staff", name) #see utils.py
        if name_error:
            messagebox.showerror("Error", name_error)
            return

        #email validation
        email_error = is_valid_email(email, self.app.session) #see utils.py
        if email_error:
            messagebox.showerror("Error", email_error)
            return

        #password validation
        password_error = is_valid_password(password1, password2) #see utils.py
        if password_error:
            messagebox.showerror("Error", password_error)
            return
        
        try:
            #hash the password
            hashed_password = ph.hash(password1)

            #get the role object from the database
            role_obj = self.app.session.query(Role).filter_by(title=role).first()

            #get the cinema id from the dropdown selections
            cinema_id = self.cinema_map[cinema]

            #create a new staff object with the details entered
            new_staff = Staff(name=name, email=email, password=hashed_password, role=role_obj, cinema_id=cinema_id)

            #add the new staff to the session (database) and commit
            self.app.session.add(new_staff)
            self.app.session.commit()

            messagebox.showinfo("Success", "Staff member added successfully.")

            from manage_staff import ManageStaffPage
            self.app.show_page(ManageStaffPage)

        except Exception as e:
            #rollback if error occurs
            self.app.session.rollback()
            messagebox.showerror("Error", f"Error! Please try again.")

    
