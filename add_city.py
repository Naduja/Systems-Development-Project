#add city page

#import here
import tkinter as tk
from tkinter import messagebox
from models import City
import re
from PIL import Image, ImageTk

class AddCityPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(bg="white", padx=130, pady=40)
        
        image = Image.open("i4.jpg") 
        image = image.resize((800, 600))  
        self.photo = ImageTk.PhotoImage(image)  
        image_label = tk.Label(self, image=self.photo, bg="white")
        image_label.grid(row=0, column=0, rowspan=15, padx=80, pady=80)  

        #frontend
        tk.Label(self, text="Add a New City", font=("Arial", 20)).grid(row=0, column=1, pady=(60, 30))

        #add city form
        tk.Label(self, text="City Name:", font=("Arial", 14)).grid(row=1, column=1, sticky="w", padx=10)
        self.name_entry = tk.Entry(self, font=("Arial", 14),width=25, relief="solid", bd=1)
        self.name_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(self, text="Morning Price:", font=("Arial", 14)).grid(row=3, column=1, sticky="w", padx=10)
        self.morning_price_entry = tk.Entry(self, font=("Arial", 14),width=25, relief="solid", bd=1)
        self.morning_price_entry.grid(row=4, column=1, padx=10, pady=5)
        
        tk.Label(self, text="Afternoon Price:", font=("Arial", 14)).grid(row=5, column=1, sticky="w", padx=10)
        self.afternoon_price_entry = tk.Entry(self, font=("Arial", 14),width=25, relief="solid", bd=1)
        self.afternoon_price_entry.grid(row=6, column=1, padx=10, pady=5)

        tk.Label(self, text="Evening Price:", font=("Arial", 14)).grid(row=7, column=1, sticky="w", padx=10)
        self.evening_price_entry = tk.Entry(self, font=("Arial", 14),width=25, relief="solid", bd=1)
        self.evening_price_entry.grid(row=8, column=1, padx=10, pady=5)
 
        #add city button
        tk.Button(self, text="Add City", font=("Arial", 14), command=self.add_city).grid(row=9, column=1, sticky="w", padx=10)
        
        #import here to avoid circular import error
        from add_cinema import AddCinemaPage
        tk.Button(self, text="Back", font=("Arial", 14), command=lambda: self.app.show_page(AddCinemaPage)).grid(row=9, column=2, sticky="w", padx=10)


    def add_city(self):
        #get form values entered by user .strip() = remove leading/trailing whitespace to avoid issues in validation
        name = self.name_entry.get().strip()
        morning_price = self.morning_price_entry.get().strip()
        afternoon_price = self.afternoon_price_entry.get().strip()
        evening_price = self.evening_price_entry.get().strip()

        #validation

        #if one of the details is missing then return error message
        if not name or not morning_price or not afternoon_price or not evening_price:
            messagebox.showerror("Error", "Please enter all details")
            return
        
        #name validation
        #if the name is more than 20 characters long return an error message
        if len(name) > 20:
            messagebox.showerror("Error", "City name cannot be more than 20 characters long")
            return
        
        #if the name is less than 2 characters long return an error message
        if len(name) < 2:
            messagebox.showerror("Error", "City name cannot be less than 2 characters long")
            return
        
        #if the name is not unique return an error message (ilike performs case-insensitive search)
        if self.app.session.query(City).filter(City.name.ilike(name)).first():
            messagebox.showerror("Error", "The city you're trying to add already exists")
            return
        
        #price validation
        #if either of the prices isn't +ve decimal(4,2) return an error message
        pattern = r'^\d{1,2}(\.\d{1,2})?$'  #regex for DECIMAL(4,2)
        if not (re.match(pattern, morning_price) and re.match(pattern, afternoon_price) and re.match(pattern, evening_price)):
            messagebox.showerror("Error", "Invalid price. Please enter a price between 0.00 and 99.99")
            return

        new_city = City(name=name, morning_price=morning_price, afternoon_price=afternoon_price, evening_price=evening_price)
        self.app.session.add(new_city)
        self.app.session.commit()
        messagebox.showinfo("Success", "City added successfully!")

        from add_cinema import AddCinemaPage
        self.app.show_page(AddCinemaPage)