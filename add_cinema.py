#add cinema page

#import here
import tkinter as tk
from tkinter import ttk
from models import Policy, SeatPricing, City, Cinema, Screen, Seat
from tkinter import messagebox
from add_city import AddCityPage
from PIL import Image, ImageTk

class AddCinemaPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="white")
        self.app = app
        
        self.grid(row=0, column=0, sticky="nsew")  # Ensure frame fills window

        # Configure grid layout for proper scaling
        self.columnconfigure(0, weight=9, minsize=450)  # 45% width for text
        self.columnconfigure(1, weight=11, minsize=550)  # 55% width for image
        self.rowconfigure(0, weight=1)  # Allow row expansion

        # TEXT/FORM SECTION
        # Create a frame to hold the text section
        text_frame = tk.Frame(self, bg="#004466")  # bg=Background color for the text section
        text_frame.grid(row=0, column=0, sticky="nsew")  # Stetches in the entire area

        #frontend
        tk.Label(text_frame, text="Add a New Cinema",fg="white", bg="#004466", font=("Arial", 20)).pack(pady=40)

        #add cinema form

        #city selection
        tk.Label(text_frame, text="City:", fg="white", bg="#004466", font=("Arial", 14)).pack(fill="x",anchor="w",padx=10,pady=20)
        city_options = [city.name for city in self.app.session.query(City).all()]
        city_options = list(set(city_options))
        #print('city_option', city_options)
        self.city_dropdown = ttk.Combobox(text_frame, values=city_options, state="readonly")
        self.city_dropdown.pack(fill="x",anchor="w",padx=10,pady=20)

        #neighbourhood entry
        tk.Label(text_frame, text="Neighbourhood:", fg="white", bg="#004466", font=("Arial", 14)).pack(fill="x",anchor="w",padx=10,pady=20)
        self.neighbourhood_entry = tk.Entry(text_frame, font=("Arial", 14))
        self.neighbourhood_entry.pack(fill="x",anchor="w",padx=10,pady=10)

        #availability selection
        tk.Label(text_frame, text="Availability Status:", fg="white", bg="#004466", font=("Arial", 14)).pack(fill="x",anchor="w",padx=10,pady=20)
        availability_options = ["Available", "Unavailable"]
        self.availability_dropdown = ttk.Combobox(text_frame, values=availability_options, state="readonly")
        self.availability_dropdown.pack(fill="x",anchor="w",padx=10,pady=20)

        #adding screens here
        tk.Label(text_frame, text="Screen Information:", fg="white", bg="#004466", font=("Arial", 14)).pack(fill="x",anchor="w",padx=10,pady=30)

        # IMAGE SECTION
        # Open the image and resize it
        self.image = Image.open("i2.jpg")
        self.image = self.image.resize((1050, 800)) 
        # Convert image to Tkinter-compatible format
        self.image = ImageTk.PhotoImage(self.image)
        # Create a label with the image
        image_label = tk.Label(self, image=self.image)
        image_label.grid(row=0, column=1, sticky="n")
        
        self.screen_forms = []  #list to store all screen form widgets

        #get policy for validation
        policy = self.app.session.query(Policy).first()

        #if the policy doesn't exist then one must be added manually (extended project could include this functionality)
        if not policy:
            messagebox.showerror("Error", "Current policy not found. Please contact the database adminstrator.")
            return
        else:
            self.policy = policy

        #takes user to add city page to add a new city
        self.add_city_button = tk.Button(self, text="Add New City",command=lambda: self.app.show_page(AddCityPage),
                                       bg="white", fg="darkblue", font=("Arial", 16, "bold"),  
                                       padx=20, pady=10)
        self.add_city_button.place(x=690, y=700)

        #button to add another screen
        self.add_screen_button = tk.Button(self, text="Add Screen",command=lambda: self.add_screen_form(text_frame),
                                       bg="white", fg="darkblue", font=("Arial", 16, "bold"), 
                                       padx=20, pady=10)
        self.add_screen_button.place(x=900, y=700)

        #button to submit cinema details
        self.add_cinema_button = tk.Button(self, text="Add Cinema",command=self.add_cinema ,
                                       bg="white", fg="darkblue", font=("Arial", 16, "bold"),  
                                       padx=20, pady=10)
        self.add_cinema_button.place(x=1100, y=700)
        
        #import here to avoid circular import error
        from manage_cinemas import ManageCinemasPage
        
        # Back Button
        self.back_button = tk.Button(self, text="Back", command=lambda: self.app.show_page(ManageCinemasPage),
                                       bg="white", fg="darkblue", font=("Arial", 16, "bold"),
                                       padx=20, pady=10)
        self.back_button.place(x=470, y=20) # top left 
    
    def add_screen_form(self, text_frame):
        #if the max number of screens per cinema hasn't been reached add another screen form
        if len(self.screen_forms) < self.policy.max_screens_per_cinema:
            screen_form = tk.Frame(text_frame, bg="#004466")
            screen_form.pack(pady=10, fill="x")

            tk.Label(screen_form, text=f"Screen {len(self.screen_forms) + 1}", fg="white", bg="#004466", font=("Arial", 14, "bold")).grid(row=0, columnspan=2, pady=5)

            #fetch all the seat types from the database
            seat_types = [seat.seat_type for seat in self.app.session.query(SeatPricing).all()]
            seat_entries = {}

            #add an input field for each seat type
            for row, seat_type in enumerate(seat_types, start=1):
                tk.Label(screen_form, text=f"Number of {seat_type} Seats:", fg="white", bg="#004466", font=("Arial", 12)).grid(row=row, column=0, padx=5, pady=5, sticky="w")
                entry = tk.Entry(screen_form, font=("Arial", 12))
                entry.grid(row=row, column=1, padx=5, pady=5)
                seat_entries[seat_type] = entry

            #add a dropdown for screen availability
            tk.Label(screen_form, text="Screen Availability:", fg="white", bg="#004466", font=("Arial", 12)).grid(row=len(seat_types) + 1, column=0, padx=5, pady=5, sticky="w")
            availability_options = ["Available", "Unavailable"]
            availability_dropdown = ttk.Combobox(screen_form, values=availability_options, font=("Arial", 12), state="readonly")
            availability_dropdown.grid(row=len(seat_types) + 1, column=1, padx=5, pady=5)

            #store references to screen form widgets
            self.screen_forms.append({
                "seat_entries": seat_entries,
                "availability_dropdown": availability_dropdown
            }) #screen_forms is a list of dictionaries where each dictionary represents a single screen form
            self.back_button.place(x=545, y=20) #move back button to the right
        #otherwise return an error message and don't add another screen form
        else:
            messagebox.showerror("Error", "The maximum number of screens per cinema has been reached.")

    #function to add cinema to database
    def add_cinema(self):
        #get form values entered by user .strip() = remove leading/trailing whitespace to avoid issues in validation
        city = self.city_dropdown.get().strip()
        neighbourhood = self.neighbourhood_entry.get().strip()
        availability = self.availability_dropdown.get().strip()
        
        #vaidate city, neighbourhood and availability

        #check if all 3 fields are filled
        if not city or not neighbourhood or not availability:
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        
        #neighbourhood validation
        if len(neighbourhood) > 60:
            messagebox.showerror("Error", "Neighbourhood cannot be more than 60 characters long")
            return

        if len(neighbourhood) < 2:
            messagebox.showerror("Error", "Neighbourhood cannot be less than 2 characters long")
            return
        
        #if there is already a cinema with the same neighbourhood in the same city, return an error message
        if self.app.session.query(Cinema).join(Cinema.city).filter(City.name.ilike(city), Cinema.neighbourhood.ilike(neighbourhood)).first():
            messagebox.showerror("Error", f"A cinema in {neighbourhood} {city} already exists.")
            return

        #validate screen forms

        #if the number of screens added is less than the minimum allowed, return an error message
        if len(self.screen_forms) < self.policy.min_screens_per_cinema:
            messagebox.showerror("Error", f"You must add at least {self.policy.min_screens_per_cinema} screens.")
            return
        
        for i, screen in enumerate(self.screen_forms, start=1):
            seat_entries = screen["seat_entries"]
            screen_availability = screen["availability_dropdown"].get().strip()

            #validate seat entries
            total_seats = 0
            seat_counts = {}

            #check if seat inputs are positive integers
            for seat_type, entry in seat_entries.items():
                count = entry.get().strip()
                if not count.isdigit():
                    messagebox.showerror("Error", f"Please enter a positive integer for {seat_type} seats in Screen {i}.")
                    return

                count = int(count)
                seat_counts[seat_type] = count
                total_seats += count

            #hard validation for total number of seats - total number of seats has to be within min-max_seats_per_screen
            if total_seats > self.policy.max_seats_per_screen or total_seats < self.policy.min_seats_per_screen:
                messagebox.showerror("Error", f"Total number of seats for Screen {i} must be between {self.policy.min_seats_per_screen} and {self.policy.max_seats_per_screen}.")
                return
            
            #hard validation for number of VIP seats - VIP seats have to be within min-max_VIP
            if seat_counts["VIP"] > self.policy.max_VIP or seat_counts["VIP"] < self.policy.min_VIP:
                messagebox.showerror("Error", f"Number of VIP seats for Screen {i} must be between {self.policy.min_VIP} and {self.policy.max_VIP}.")
                return

            #soft validation for lower hall percentage
            if "Lower Hall" in seat_counts:
                lh_percentage = (seat_counts["Lower Hall"] / total_seats) * 100
                tolerance = 5
                if lh_percentage < (self.policy.lower_hall_percentage - tolerance) or lh_percentage > (self.policy.lower_hall_percentage + tolerance):
                    result = messagebox.askyesno(
                        "Warning",
                        f"The percentage of lower hall seats for Screen {i} is {lh_percentage:.2f}%, "
                        f"which is outside the general guidelines of about {self.policy.lower_hall_percentage}%. "
                        "Do you still want to proceed?"
                    )
                    if not result:
                        return

            #validate screen availability

            #check if availability field is empty
            if not screen_availability:
                messagebox.showerror("Error", f"Please select the availability status for Screen {i}.")
                return

            #validate screen availability against cinema availability
            if availability == "Unavailable" and screen_availability == "Available":
                messagebox.showerror("Error", f"Cinema is marked as unavailable, so Screen {i} cannot be available.")
                return

        #if passes all validation checks then add the cinema, and its associated screens and seats to the database
        if availability == "Available":
            available = True
        else:
            available = False

        new_cinema = Cinema(
            neighbourhood=neighbourhood,
            available=available,
            city=self.app.session.query(City).filter(City.name.ilike(city)).one()
        )

        self.app.session.add(new_cinema)
        self.app.session.commit()

        for screen in self.screen_forms:
            if screen["availability_dropdown"].get().strip() == "Available":
                screen_available = True
            else:
                screen_available = False

            new_screen = Screen(
                num_lower_gallery=screen["seat_entries"]["Lower Hall"].get().strip(),
                num_upper_gallery=screen["seat_entries"]["Upper Gallery (excl. VIP)"].get().strip(),
                num_VIP=screen["seat_entries"]["VIP"].get().strip(),
                available=screen_available,
                cinema=new_cinema
            )
            self.app.session.add(new_screen)
            self.app.session.commit()

            total_seats = int(screen["seat_entries"]["Lower Hall"].get().strip()) + int(screen["seat_entries"]["Upper Gallery (excl. VIP)"].get().strip()) + int(screen["seat_entries"]["VIP"].get().strip())

            for seat_num in range(1, total_seats + 1):
                seat_type = "Lower Hall" if seat_num <= int(screen["seat_entries"]["Lower Hall"].get().strip()) else "Upper Gallery (excl. VIP)" if seat_num <= int(screen["seat_entries"]["Lower Hall"].get().strip()) + int(screen["seat_entries"]["Upper Gallery (excl. VIP)"].get().strip()) else "VIP"
                new_seat = Seat(
                    number=seat_num,
                    available=True,
                    screen=new_screen,
                    seatpricing=self.app.session.query(SeatPricing).filter(SeatPricing.seat_type == seat_type).one()
                )
                self.app.session.add(new_seat)

        self.app.session.commit()
        messagebox.showinfo("Success", "Cinema added successfully.")
        #import here to avoid circular error
        from manage_cinemas import ManageCinemasPage
        self.app.show_page(ManageCinemasPage)
