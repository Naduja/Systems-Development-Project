#manage cinemas page

#import here
import tkinter as tk
from models import Cinema
from add_cinema import AddCinemaPage
from PIL import Image, ImageTk

class ManageCinemasPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        
        self.grid(row=0, column=0, sticky="nsew")  # Ensure frame fills window

        # Configure grid layout for proper scaling
        self.columnconfigure(0, weight=9, minsize=450)  # 45% width for text
        self.columnconfigure(1, weight=11, minsize=550)  # 55% width for image
        self.rowconfigure(0, weight=1)  # Allow row expansion

        # Text Section
        text_frame = tk.Frame(self, bg="#004466")  
        text_frame.grid(row=0, column=0, sticky="nsew")  # Stretches in its area
        
        #frontend
        tk.Label(text_frame, text="Manage Cinemas", fg="white", bg="#004466", font=("Arial", 20)).pack(pady=50)

        #list of cinemas
        #query database to get all cinema objects
        cinemas = self.app.session.query(Cinema).all()

        #if there are no cinemas then show appropriate message
        if not cinemas:
            tk.Label(text_frame, text="Get Started by Adding a Cinema!", fg="white", bg="#004466", font=("Arial", 12)).pack(pady=20)
        #otherwise loop through the list of cinemas and display their details
        else:
            for cinema in cinemas:
                cinema_details = f"Horizon Cinemas {cinema.city.name} {cinema.neighbourhood} | Available: {cinema.available}"
                tk.Label(text_frame, text=cinema_details, bg="#004466", fg="white", font=("Arial", 12)).pack(pady=10)

        #add cinema button
        tk.Button(text_frame, text="Add a New Cinema", font=("Arial", 14), command=lambda: self.app.show_page(AddCinemaPage)).pack(pady=50)

        # Image Section
        # Open the image and resize it
        self.image = Image.open("i3.png")
        self.image = self.image.resize((1050, 800))
        # Convert image to Tkinter-compatible format
        self.image = ImageTk.PhotoImage(self.image)
        # Create a label with the image
        image_label = tk.Label(self, image=self.image)
        image_label.grid(row=0, column=1, sticky="nsew")  # Stretches in its area

        #import here to avoid circular import error
        from main_menu import MainMenuPage

        # Back Button
        self.back_button = tk.Button(self, text="Back", command=lambda: self.app.show_page(MainMenuPage),
                                       bg="white", fg="darkblue", font=("Arial", 16, "bold"), padx=20, pady=10)
        self.back_button.place(x=470, y=20) # position at top left corner





