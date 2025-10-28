#cancel booking page

#import here
import tkinter as tk
from tkinter import messagebox
from models import Booking, Policy
from datetime import datetime, timedelta
from sqlalchemy import func
from PIL import Image, ImageTk

class CancelBookingPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(bg="white", padx=130, pady=40)
        
        image = Image.open("i6.jpg") 
        image = image.resize((800, 600))  
        self.photo = ImageTk.PhotoImage(image)  
        image_label = tk.Label(self, image=self.photo, bg="white")
        image_label.grid(row=0, column=0, rowspan=15, padx=80, pady=80) 

        #frontend
        tk.Label(self, text="Cancel a Booking", font=("Arial", 20)).grid(row=0, column=1, pady=(60, 30))

        #cancel booking form
        tk.Label(self, text="Booking Reference:", font=("Arial", 14)).grid(row=1, column=1, sticky="w", padx=10)
        self.reference_entry = tk.Entry(self, font=("Arial", 14),width=25, relief="solid", bd=1)
        self.reference_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(self, text="Booking Date (DD/MM/YY):", font=("Arial", 14)).grid(row=3, column=1, sticky="w", padx=10)
        self.date_entry = tk.Entry(self, font=("Arial", 14),width=25, relief="solid", bd=1)
        self.date_entry.grid(row=4, column=1, padx=10, pady=5)

        tk.Button(self, text="Cancel Booking", font=("Arial", 14), command=self.cancel_booking).grid(row=9, column=1, sticky="w", padx=10)
        
        #import here to avoid circular import error
        from main_menu import MainMenuPage
        tk.Button(self, text="Back", font=("Arial", 14), command=lambda: self.app.show_page(MainMenuPage)).grid(row=9, column=2, sticky="w", padx=10)

    def cancel_booking(self):
        #get form values
        reference_number = self.reference_entry.get().strip()
        date = self.date_entry.get().strip()

        #check if any of the form details are missing
        if not all([reference_number, date]):
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        
        #check if the date entry is in the right format
        try:
            booking_date = datetime.strptime(date, "%d/%m/%y").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use DD/MM/YY.")
            return
        
        #check if a booking with booking_id reference_number exists
        booking = self.app.session.query(Booking).filter(
            Booking.booking_id == reference_number, 
            func.date(Booking.booking_date) == booking_date
        ).first()

        if not booking:
            messagebox.showerror("Error", "Booking not found.")
            return
        
        #check if the booking has already been cancelled
        if booking.cancelled:
            messagebox.showerror("Error", "This booking has already been cancelled.")
            return

        #fetch current policy
        policy = self.app.session.query(Policy).first()

        if not policy:
            messagebox.showerror("Error", "No policy found. Please contact the database adminstrator.")
            return

        #if the current date is at least min_days_for_refund before the showing date then allow cancellation
        refund_cutoff_date = booking.showing.start_time - timedelta(days=policy.min_days_for_refund)

        if datetime.now() > refund_cutoff_date:
            messagebox.showerror("Error", "The cancellation period has passed. No refund available.")
            return
        
        #ask for confirmation
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to cancel this booking?")
        if not confirm:
            return

        #mark booking as cancelled
        booking.cancelled = True

        #set the refund amount
        booking.refund_amount = (booking.booking_cost * policy.refund_percentage) / 100

        #commit changes
        self.app.session.commit()

        messagebox.showinfo("Success", "Booking has been successfully cancelled.")
        from main_menu import MainMenuPage
        self.app.show_page(MainMenuPage)


        
