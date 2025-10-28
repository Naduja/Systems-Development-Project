#payment page

#import here
import tkinter as tk
from tkinter import messagebox
from utils import is_valid_name, is_valid_email, is_valid_phone, is_valid_card, get_available_seats
from datetime import datetime
from models import Booking, BookingSeat
from PIL import Image, ImageTk

class PaymentPage(tk.Frame):
    def __init__(self, parent, app, showing_obj, ticket_type, total_price, ticket_count):
        super().__init__(parent)
        self.app = app
        self.showing_obj = showing_obj
        self.ticket_type = ticket_type
        self.total_price = total_price
        self.ticket_count = ticket_count

        self.grid(row=0, column=0, sticky="nsew")  # Ensure frame fills window

        # Configure grid layout for proper scaling
        self.columnconfigure(0, weight=9, minsize=450)  # 45% width for text
        self.columnconfigure(1, weight=11, minsize=550)  # 55% width for image
        self.rowconfigure(0, weight=1)  # Allow row expansion
        
        # Text Section
        text_frame = tk.Frame(self, bg="#004466")  
        text_frame.grid(row=0, column=0, sticky="nsew")  # Stretches in its area

        #frontend
        tk.Label(text_frame, text="Payment", font=("Arial", 20), fg="white", bg="#004466").pack(pady=30)
       
        #payment form
        tk.Label(text_frame, text="Full Name:", font=("Arial", 14), fg="white", bg="#004466").pack(fill="x", padx=10,pady=10)
        self.name_entry = tk.Entry(text_frame, font=("Arial", 14))
        self.name_entry.pack(padx=10,pady=5)

        tk.Label(text_frame, text="Email Address:", font=("Arial", 14), fg="white", bg="#004466").pack(fill="x", padx=10,pady=10)
        self.email_entry = tk.Entry(text_frame, font=("Arial", 14))
        self.email_entry.pack(padx=10,pady=5)

        tk.Label(text_frame, text="Phone Number:", font=("Arial", 14), fg="white", bg="#004466").pack(fill="x", padx=10,pady=10)
        self.phone_entry = tk.Entry(text_frame, font=("Arial", 14))
        self.phone_entry.pack(padx=10,pady=5)

        tk.Label(text_frame, text="Card Number:", font=("Arial", 14), fg="white", bg="#004466").pack(fill="x",padx=10,pady=10)
        self.card_entry = tk.Entry(text_frame, font=("Arial", 14))
        self.card_entry.pack(padx=10,pady=5)

        tk.Label(text_frame, text="Expiry Date (MM/YY):", font=("Arial", 14), fg="white", bg="#004466").pack(fill="x",padx=10,pady=10)
        self.expiry_entry = tk.Entry(text_frame, font=("Arial", 14))
        self.expiry_entry.pack(padx=10,pady=5)

        tk.Label(text_frame, text="CVV:", font=("Arial", 14), fg="white", bg="#004466").pack(fill="x",padx=10,pady=10)
        self.cvv_entry = tk.Entry(text_frame, font=("Arial", 14), show="*")
        self.cvv_entry.pack(padx=10,pady=5)

        tk.Button(text_frame, text="Book Now", font=("Arial", 14), command=self.book).pack(padx=10,pady=10)

        # Open the image and resize it
        self.image = Image.open("img8.jpg")
        self.image = self.image.resize((1200, 800))
        # Convert image to Tkinter-compatible format
        self.image = ImageTk.PhotoImage(self.image)
        # Create a label with the image
        image_label = tk.Label(self, image=self.image)
        image_label.grid(row=0, column=1, sticky="nsew")  # Stretches in its area
        
        #import here to avoid circular import error
        from book_tickets import BookTicketsPage
        self.back_button = tk.Button(self, text="Back", command=lambda: self.app.show_page(BookTicketsPage),
                                       bg="white", fg="darkblue", font=("Arial", 16, "bold"), padx=20, pady=10)
        self.back_button.place(x=470, y=20) # position at top left corner

    def book(self):
        #get form values
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        #sensitive - don't strip
        card_number = self.card_entry.get()
        expiry = self.expiry_entry.get()
        cvv = self.cvv_entry.get()

        #check if any of the details are missing
        if not all([name, email, phone, card_number, expiry, cvv]):
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        
        #validation
        #name validation
        name_error = is_valid_name("Customer", name) #see utils.py
        if name_error:
            messagebox.showerror("Error", name_error)
            return

        #email validation
        email_error = is_valid_email(email, self.app.session) #see utils.py
        if email_error:
            messagebox.showerror("Error", email_error)
            return
        
        #phone validation
        phone_error = is_valid_phone(phone)
        if not phone_error:
            messagebox.showerror("Error", 'Please enter a valid phone number.')
            return
        
        #card validation
        card_error = is_valid_card(card_number, expiry, cvv)
        if card_error:
            messagebox.showerror("Error", card_error)
            return
        
        #if all checks pass make booking

        #values passed in through book tickets
        showing_id = self.showing_obj.showing_id
        booking_cost = self.total_price

        #create a new booking
        new_booking = Booking(
            customer_name=name,
            customer_email=email,
            customer_phone=phone,
            booking_date=datetime.now(),
            booking_cost=booking_cost,
            cancelled=False,
            showing_id=showing_id,
            staff_id=self.app.user.staff_id
        )

        #add booking to the session
        session = self.app.session
        session.add(new_booking)
        session.flush()  #flush to get booking_id

        #get available seats
        available_seats = get_available_seats(self.app.session, self.showing_obj, self.ticket_type)

        #add related BookingSeat entries
        for seat in available_seats[:self.ticket_count]: #select the first ticket_count available seats
            booking_seat = BookingSeat(
                booking_id=new_booking.booking_id,
                seat_id=seat.seat_id
            )
            session.add(booking_seat)
        
        #commit changes
        session.commit()
        
        #success message
        messagebox.showinfo("Success", "Booking completed successfully!")
        
        #go to receipt page
        from receipt import ReceiptPage
        self.app.show_page(ReceiptPage, booking=new_booking)
