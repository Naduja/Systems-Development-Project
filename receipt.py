#receipt page

#import here
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class ReceiptPage(tk.Frame):
    def __init__(self, parent, app, booking):
        super().__init__(parent)
        self.app = app
        self.user = self.app.user
        
        self.grid(row=0, column=0, sticky="nsew")  # Ensure frame fills window

        # Configure grid layout for proper scaling
        self.columnconfigure(0, weight=9, minsize=450)  # 45% width for text
        self.columnconfigure(1, weight=11, minsize=550)  # 55% width for image
        self.rowconfigure(0, weight=1)  # Allow row expansion

        # Text Section
        text_frame = tk.Frame(self, bg="#004466")  
        text_frame.grid(row=0, column=0, sticky="nsew")  # Stretches in its area

        #frontend
        tk.Label(text_frame, text="Receipt", font=("Arial", 20), fg="white", bg="#004466").pack(pady=30)

        tk.Label(text_frame, text=f"Booking Reference: {booking.booking_id}", font=("Arial", 14), fg="white", bg="#004466").pack(fill="x",padx=10,pady=10)
        tk.Label(text_frame, text=f"Location: {booking.showing.screen.cinema.neighbourhood} {booking.showing.screen.cinema.city.name}", font=("Arial", 14), fg="white", bg="#004466").pack(fill="x",padx=10,pady=10)
        tk.Label(text_frame, text=f"Film: {booking.showing.film.name} ({booking.showing.film.release_year})", font=("Arial", 14), fg="white", bg="#004466").pack(fill="x",padx=10,pady=10)
        tk.Label(text_frame, text=f"Air Date: {booking.showing.start_time.date().strftime('%d/%m/%Y')}", font=("Arial", 14), fg="white", bg="#004466").pack(fill="x",padx=10,pady=10)
        tk.Label(text_frame, text=f"Showing Time: {booking.showing.start_time.strftime('%H:%M')} - {booking.showing.end_time.strftime('%H:%M')}", font=("Arial", 14), fg="white", bg="#004466").pack(fill="x",padx=10,pady=10)
        tk.Label(text_frame, text=f"Screen No.: {booking.showing.screen.screen_id}", font=("Arial", 14), fg="white", bg="#004466").pack(fill="x",padx=10,pady=10)

        #get list of seat numbers
        seat_numbers = [seat.seat.number for seat in booking.bookingseats]
        #convert into a string e.g. "1, 2, 3"
        seat_list = ", ".join(map(str, seat_numbers))

        tk.Label(text_frame, text=f"No. of Tickets: {len(seat_numbers)}", font=("Arial", 14), fg="white", bg="#004466").pack(fill="x",padx=10,pady=10)
        tk.Label(text_frame, text=f"Seats: {seat_list}", font=("Arial", 14), fg="white", bg="#004466").pack(fill="x",padx=10,pady=10)
        tk.Label(text_frame, text=f"Booking Cost: £{booking.booking_cost:.2f}", font=("Arial", 14), fg="white", bg="#004466").pack(fill="x",padx=10,pady=10)
        tk.Label(text_frame, text=f"Date Booked: {booking.booking_date.strftime('%d/%m/%Y %H:%M')}", font=("Arial", 14), fg="white", bg="#004466").pack(fill="x",padx=10,pady=10)

        #go back to book tickets page
        from book_tickets import BookTicketsPage
        tk.Button(text_frame, text="Book Another Ticket", font=("Arial", 14), command=lambda: self.app.show_page(BookTicketsPage)).pack(padx=10,pady=10)

        from main_menu import MainMenuPage
        tk.Button(text_frame, text="Main Menu", font=("Arial", 14), command=lambda: self.app.show_page(MainMenuPage)).pack(padx=10,pady=10)

        # Open the image and resize it
        self.image = Image.open("img8.jpg")
        self.image = self.image.resize((1200, 800))
        # Convert image to Tkinter-compatible format
        self.image = ImageTk.PhotoImage(self.image)
        # Create a label with the image
        image_label = tk.Label(self, image=self.image)
        image_label.grid(row=0, column=1, sticky="nsew")  # Stretches in its area