#book tickets page

#import here
import tkinter as tk
from tkinter import messagebox
from models import Film, Screen, Showing, Cinema, SeatPricing, Policy
from datetime import datetime, timedelta
from sqlalchemy import func
from utils import validate_spinbox, MyCalendar, get_available_seats
from payment import PaymentPage
from PIL import Image, ImageTk

class BookTicketsPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.user = self.app.user
        self.user_role = self.user.role.title

        self.grid(row=0, column=0, sticky="nsew")  # Ensure frame fills window

        # Configure grid layout for proper scaling
        self.columnconfigure(0, weight=9, minsize=450)  # 45% width for text
        self.columnconfigure(1, weight=11, minsize=550)  # 55% width for image
        self.rowconfigure(0, weight=1)  # Allow row expansion
        
        # Text Section
        text_frame = tk.Frame(self, bg="#004466")  
        text_frame.grid(row=0, column=0, sticky="nsew")  # Stretches in its area

        #frontend
        tk.Label(text_frame, text="Book Tickets", font=("Arial", 20), bg="#004466", fg="white").pack(pady=10)

        #BOOKING FORM
        #if the user is admin/manager allow them to select a cross-chain cinema
        if self.user_role.lower() != "booking staff":
            #CINEMA SELECTION
            tk.Label(text_frame, text="Cinema:", font=("Arial", 14), bg="#004466", fg="white").pack(pady=10)
            #set cinema options to all the cinemas from the database
            cinema_options = [f"{cinema.neighbourhood} {cinema.city.name}" for cinema in self.app.session.query(Cinema).all()]
            self.cinema_selected_option = tk.StringVar()
            self.cinema_selected_option.set(cinema_options[0])
            self.cinema_dropdown = tk.OptionMenu(text_frame, self.cinema_selected_option, *cinema_options)
            self.cinema_dropdown.pack(pady=5)
        else:
            self.cinema_selected_option = tk.StringVar()
            self.cinema_selected_option.set(f"{self.user.cinema.neighbourhood} {self.user.cinema.city.name}")

        #FILM SELECTION
        tk.Label(text_frame, text="Film:", font=("Arial", 14), bg="#004466", fg="white").pack(pady=10)
        self.film_selected_option = tk.StringVar()

        #if the user is booking staff then film dropdown isn't dependent on a cinema being selected
        if self.user_role.lower() == "booking staff":
            #set the dropdown options to the films being showed at the user's cinema that have a showing in the future
            film_options = [f"{film.name} ({film.release_year})" for film in self.app.session.query(Film).join(Showing).join(Screen)
                            .filter(
                                Screen.cinema.has(cinema_id=self.user.cinema.cinema_id), #screen has to be in the user's cinema
                                Showing.start_time > datetime.now()  #showing has to be in the future
                            )
                            .distinct()  #avoid duplicate films
                            .all()
                        ]
            
            #set the default selected option to the first option
            self.film_selected_option.set(film_options[0])
            #film dropdown
            self.film_dropdown = tk.OptionMenu(text_frame, self.film_selected_option, *film_options)
        #otherwise if the user is admin/manager then film dropdown is dependent on a cinema being selected
        else:
            #init empty dropdown
            self.film_dropdown = tk.OptionMenu(text_frame, self.film_selected_option, [])
            #initialise film dropdown options on first load (before changes are made to cinema selected)
            self.update_film_options()

            #attach a trace callback to cinema_dropdown so that when a cinema is selected update_film_options is called and the film options are updated
            self.cinema_selected_option.trace_add("write", lambda *args: self.update_film_options())

        self.film_dropdown.pack(pady=5)

        #DATE SELECTION
        tk.Label(text_frame, text="Date:", font=("Arial", 14), bg="#004466", fg="white").pack(pady=10)
        self.calendar = MyCalendar(text_frame, selectmode='day', year=datetime.now().year, month=datetime.now().month, disableddaybackground="red")
        self.calendar.pack(pady=5)

        #initialise date options on first load (before changes are made to cinema/film selected)
        self.update_date_options()

        #SHOW TIME SELECTION
        tk.Label(text_frame, text="Show Time:", font=("Arial", 14), bg="#004466", fg="white").pack(pady=10)
        self.show_time_selected_option = tk.StringVar()
        self.show_time_dropdown = tk.OptionMenu(text_frame, self.show_time_selected_option, [])
        self.show_time_dropdown.pack(pady=5)

        #initialise show time options on first load (before changes are made to cinema/film/date selected)
        self.update_show_time_options()

        #TYPE AND NUMBER OF TICKETS SELECTION
        tk.Label(text_frame, text="Type of Tickets:", font=("Arial", 14), bg="#004466", fg="white").pack(pady=10)
        #set ticket type options to all the seat types from the database
        ticket_type_options = [f"{seatpricing.seat_type}" for seatpricing in self.app.session.query(SeatPricing).all()]
        self.ticket_type_selected_option = tk.StringVar()
        self.ticket_type_selected_option.set(ticket_type_options[0])
        self.ticket_type_dropdown = tk.OptionMenu(text_frame, self.ticket_type_selected_option, *ticket_type_options)
        self.ticket_type_dropdown.pack(pady=5)

        self.available_seats = [1] #default to 1 seat available at the start then updated when showing selected
        #register validation function for ticket spinbox
        vcmd = (self.app.root.register(lambda input: validate_spinbox(input, len(self.available_seats))), "%P")
        tk.Label(text_frame, text="Number of Tickets:", font=("Arial", 14), bg="#004466", fg="white").pack(pady=10)
        self.ticket_count = tk.IntVar(value=1)
        self.ticket_spinbox = tk.Spinbox(text_frame, from_=1, to=10, wrap=False, width=3, textvariable=self.ticket_count, validate="key", validatecommand=vcmd)
        self.ticket_spinbox.pack(pady=5)

        #AVAILABILITY AND PRICE DISPLAY
        self.availability_label = tk.Label(text_frame, text="Availability: Checking...", font=("Arial", 14), bg="#004466", fg="white")
        self.availability_label.pack(pady=10)

        self.price_label = tk.Label(text_frame, text="Price: Calculating...", font=("Arial", 14), bg="#004466", fg="white")
        self.price_label.pack(pady=10)

        #CHECKOUT BUTTON - initially set as disabled then enable when booking passes initial validation
        self.proceed_button = tk.Button(text_frame, text="Proceed to Payment", font=("Arial", 14), state=tk.DISABLED, command=self.validate_booking)
        self.proceed_button.pack(padx=10,pady=10)

        # IMAGE SECTION
        self.image = Image.open("img11.jpg")
        self.image = self.image.resize((1200, 900))
        # Convert image to Tkinter-compatible format
        self.image = ImageTk.PhotoImage(self.image)
        # Create a label with the image
        image_label = tk.Label(self, image=self.image)
        image_label.grid(row=0, column=1, sticky="nsew")  # Stretches in its area
        
        #import here to avoid circular import error
        from main_menu import MainMenuPage
        # Back Button
        self.back_button = tk.Button(self, text="Back", command=lambda: self.app.show_page(MainMenuPage),
                                       bg="white", fg="darkblue", font=("Arial", 16, "bold"),
                                       padx=20, pady=10)
        self.back_button.place(x=470, y=20) # top left 

        #bind events
        self.ticket_count.trace_add("write", lambda *args: self.update_ticket_max())
        self.ticket_type_selected_option.trace_add("write", lambda *args: self.update_ticket_max())
        self.show_time_selected_option.trace_add("write", lambda *args: self.update_ticket_max())
        self.calendar.bind("<<CalendarSelected>>", lambda event: self.update_show_time_options(), self.update_ticket_max())
        self.film_selected_option.trace_add("write", lambda *args: [self.update_date_options(), self.update_show_time_options(), self.update_ticket_max()])
        self.cinema_selected_option.trace_add("write", lambda *args: [self.update_film_options(), self.update_date_options(), self.update_ticket_max()])

    #function to update film options dropdown based on selected cinema
    def update_film_options(self):
        #get the selected cinema's name
        selected_cinema_name = self.cinema_selected_option.get().strip()
        #split neighbourhood and city name from the selected cinema's name to filter Cinema table
        selected_neighbourhood, selected_city_name = selected_cinema_name.rsplit(" ", 1)

        #get the selected cinema's object
        selected_cinema = self.app.session.query(Cinema).join(Cinema.city).filter(Cinema.neighbourhood == selected_neighbourhood, Cinema.city.has(name=selected_city_name)).first()

        #get all films for selected cinema that have a showing in the future
        film_options = [f"{film.name} ({film.release_year})" for film in self.app.session.query(Film).join(Showing).join(Screen)
                        .filter(
                            Screen.cinema.has(cinema_id=selected_cinema.cinema_id), #screen has to be in the selected cinema
                            Showing.start_time > datetime.now()  #showing has to be in the future
                        )
                        .distinct()  #avoid duplicate films
                        .all()
                    ]

        #clear and update the film dropdown menu with the new options
        menu = self.film_dropdown["menu"]
        menu.delete(0, "end")

        for option in film_options:
            menu.add_command(label=option, command=lambda value=option: self.film_selected_option.set(value))

        #set the first option as the default (if available)
        if film_options:
            self.film_selected_option.set(film_options[0])
            self.update_date_options()
        else:
            self.film_selected_option.set("No Films Available")
    
    #function to update date options dropdown based on selected cinema and film
    def update_date_options(self):
        #make sure the calendar has been initialised
        if not hasattr(self, "calendar"):
            return  #if it hasn't then exit

        #check if a cinema and film have been selected
        selected_cinema_name = self.cinema_selected_option.get().strip()
        selected_film_name = self.film_selected_option.get().strip()

        #if no cinema or film has been selected disable all dates and return
        if not selected_cinema_name or "No Films Available" in selected_film_name:
            #reset the calendar
            self.calendar._disabled_dates.clear()
            self.calendar.selection_clear()

            #disable all dates
            for month in range(1, 13):
                for day in range(1, 32):
                    try:
                        date_check = datetime(datetime.now().year, month, day).date()
                        self.calendar.disable_date(date_check)
                    except ValueError:
                        continue  #skip invalid days (e.g. 31st of February)
            self.calendar.update_idletasks()  #refresh UI
            return  #exit early since no valid dates exist

        #if there is a valid cinema and film selected, proceed to enable the available dates
        #get film name and year by separating using split
        selected_film_name, selected_film_year = selected_film_name.rsplit(" (", 1)
        selected_film_year = selected_film_year.rstrip(")")  #remove closing bracket

        #get the selected cinema object
        selected_neighbourhood, selected_city_name = selected_cinema_name.rsplit(" ", 1)
        selected_cinema = self.app.session.query(Cinema).join(Cinema.city).filter(
            Cinema.neighbourhood == selected_neighbourhood,
            Cinema.city.has(name=selected_city_name)
        ).first()

        #get available showings for the selected film at the selected cinema
        available_showings = self.app.session.query(Showing.start_time).join(Screen).join(Film).filter(
            Screen.cinema.has(cinema_id=selected_cinema.cinema_id),
            Film.name == selected_film_name,
            Film.release_year == selected_film_year,
            Showing.start_time > datetime.now()
        ).all()

        #shouldn't happen since only films with available showings should be in the dropdown
        if not available_showings:
            messagebox.showerror("No Dates", "No available show dates for the selected film.")
            return

        #get the min and max dates from the available showings
        min_date = min(available_showings, key=lambda x: x[0])[0].date()
        max_date = max(available_showings, key=lambda x: x[0])[0].date()

        #set the calendar's min and max date based on the min and max dates of the available showings
        self.calendar.config(
            mindate=min_date,
            maxdate=max_date
        )

        #reset disabled dates and clear previous selections
        self.calendar._disabled_dates.clear()
        self.calendar.selection_clear()

        #get the available dates
        available_dates = {showing.start_time.date() for showing in available_showings}

        #if the date is not in the available dates, disable it
        for month in range(1, 13):
            for day in range(1, 32):
                try:
                    date_check = datetime(datetime.now().year, month, day).date()
                    if date_check not in available_dates: #if not in available dates
                        self.calendar.disable_date(date_check) #disable the date
                except ValueError:
                    continue  #skip invalid days (e.g. 31st of February)

        #refresh UI
        self.calendar.update_idletasks()

        #display updated calendar
        self.calendar._display_calendar()

    #function to update showtime options dropdown based on selected cinema, film, and date
    def update_show_time_options(self):
        #get the selected cinema, film, and date
        selected_cinema_name = self.cinema_selected_option.get().strip()
        selected_film_name = self.film_selected_option.get().strip()
        selected_date = self.calendar.get_date()

        #if no cinema/film/date has been selected, clear the showtime dropdown
        if not selected_cinema_name or "No Films Available" in selected_film_name or not selected_date:
            menu = self.show_time_dropdown["menu"]
            menu.delete(0, "end")
            self.show_time_selected_option.set("")
            self.show_time_dict = {}
            return  #exit early since there is no valid selection

        #split the film name to get the year and name separately
        selected_film_name, selected_film_year = selected_film_name.rsplit(" (", 1)
        selected_film_year = selected_film_year.rstrip(")")

        #split the cinema name into neighbourhood and city
        selected_neighbourhood, selected_city_name = selected_cinema_name.rsplit(" ", 1)

        #get the selected cinema object
        selected_cinema = self.app.session.query(Cinema).join(Cinema.city).filter(
            Cinema.neighbourhood == selected_neighbourhood,
            Cinema.city.has(name=selected_city_name)
        ).first()

        #convert selected date from mm/dd/yy to yyyy-mm-dd
        selected_date = datetime.strptime(selected_date, "%m/%d/%y").strftime("%Y-%m-%d")

        #get available showings for the selected film at the selected cinema on the selected date
        available_showings = self.app.session.query(Showing).join(Screen).join(Film).filter(
            Screen.cinema.has(cinema_id=selected_cinema.cinema_id), #screen has to be in the selected cinema
            Film.name == selected_film_name, #film has to be the selected film
            Film.release_year == selected_film_year, #film has to be the selected film
            func.date(Showing.start_time) == selected_date  #showing has to be on the selected date
        ).all()

        #if there are no available showings for the selected date, clear the showtime dropdown
        if not available_showings:
            messagebox.showerror("No Showings", "No showings available for the selected date.")
            menu = self.show_time_dropdown["menu"]
            menu.delete(0, "end")
            self.show_time_selected_option.set("")
            self.show_time_dict = {}
            return
        
        #store showtime options and corresponding showing_ids in a dictionary (to be easily accessed later)
        self.show_time_dict = {
            f"{showing.start_time.strftime('%H:%M')} - {showing.end_time.strftime('%H:%M')}": showing
            for showing in available_showings
        }

        #clear and update the show time dropdown menu with the new options (the dict keys are the options)
        menu = self.show_time_dropdown["menu"]
        menu.delete(0, "end")

        for option in self.show_time_dict.keys():
            menu.add_command(label=option, command=lambda value=option: self.show_time_selected_option.set(value))

        #set the first option as the default (if available)
        if self.show_time_dict:
            first_showtime = next(iter(self.show_time_dict))  #get the first dict key
            self.show_time_selected_option.set(first_showtime)

    #function to update the ticket spinbox's max based on selected ticket_type, showtime and cinema
    def update_ticket_max(self):
        #get the selected ticket type, showing and cinema
        selected_ticket_type = self.ticket_type_selected_option.get().strip()
        selected_showing =  self.show_time_selected_option.get().strip()
        selected_cinema_name = self.cinema_selected_option.get().strip()

        #if no showing has been selected yet then set max to default 1, update availability and price and disable proceed button
        if not selected_showing:
            self.ticket_spinbox.config(to=1)
            self.availability_label.config(text="Availability: Select a Date and Time to See Availability")
            self.price_label.config(text="Price: Select a Date and Time to See Price")
            self.proceed_button.config(state=tk.DISABLED)
            return
        
        #get the selected showing's object from the show_time dict
        showing_obj = self.show_time_dict.get(selected_showing, None)

        #get a list of the available seats using the get_available_seats function
        self.available_seats = get_available_seats(self.app.session, showing_obj, selected_ticket_type)
        
        #if there are no available seats
        if len(self.available_seats) == 0:
            #disable spinbox
            self.ticket_spinbox.config(to=1, state=tk.DISABLED)
            #set availability to sold out
            self.availability_label.config(text="Availability: Sold Out")
            #set price to N/A
            self.price_label.config(text="Price: N/A")
            #disable the proceed to payment button
            self.proceed_button.config(state=tk.DISABLED)
            return
        
        #otherwise set the max to the number of available seats
        self.ticket_spinbox.config(to=len(self.available_seats), state=tk.NORMAL)

        #if there are seats available then update availability and price and enable the proceed button
        if len(self.available_seats) > 0:
            #get the hour of the start time of the selected showing
            start_time = selected_showing.split(" - ")[0]  #extracts start time e.g. "14:00" if "14:00 - 16:00"
            hour = int(start_time.split(":")[0])  #extracts the hour e.g. "14" if "14:00"
            
            #if the user is booking staff then the cinema is the user's cinema otherwise it's the selected cinema
            if self.user_role.lower() == "booking staff":
                cinema = self.user.cinema
            else:
                #split the cinema name into neighbourhood and city
                selected_neighbourhood, selected_city_name = selected_cinema_name.rsplit(" ", 1)

                #get the selected cinema object
                cinema = self.app.session.query(Cinema).join(Cinema.city).filter(
                    Cinema.neighbourhood == selected_neighbourhood,
                    Cinema.city.has(name=selected_city_name)
                ).first()

            #calculate whether the show time selected is morning (08:00 - 11:59), afternoon (12:00 - 16:59) or evening (17:00 - 23:59)
            #and get the cinema's price for the time frame selected
            if 8 <= hour < 12:
                time_price = cinema.city.morning_price
            elif 12 <= hour < 17:
                time_price = cinema.city.afternoon_price
            else:
                time_price = cinema.city.evening_price

            #get the seat pricing for the ticket type selected
            seat_pricing = self.app.session.query(SeatPricing).filter(SeatPricing.seat_type == selected_ticket_type).first()

            #if the number of tickets hasn't been entered then disable the proceed button and return
            try:
                num_tickets = int(self.ticket_spinbox.get().strip())
            except ValueError:
                self.price_label.config(text=f"Price: Calculating...")
                self.proceed_button.config(state=tk.DISABLED)
                return

            #calculate the total price of tickets by multiplying the time price by the seat pricing and the number of tickets
            self.total_price = time_price * seat_pricing.multiplier * num_tickets

            #display the total number of seats available
            self.availability_label.config(text=f"Availability: {len(self.available_seats)} seats available")
            #display the total calculated price
            self.price_label.config(text=f"Total Price: £{self.total_price:.2f}")
            #enable the proceed button
            self.proceed_button.config(state=tk.NORMAL)
        #otherwise if there are no seats available then update availability and disable the proceed button
        else:
            self.availability_label.config(text="Availability: Sold Out")
            self.proceed_button.config(state=tk.DISABLED)

    #validate booking options before proceeding to payment
    def validate_booking(self):
        #get form values entered by user
        cinema = self.cinema_selected_option.get().strip()
        film = self.film_selected_option.get().strip()
        date = self.calendar.get_date().strip()
        show_time = self.show_time_selected_option.get().strip()
        ticket_type = self.ticket_type_selected_option.get().strip()
        ticket_count = self.ticket_count.get()

        #check if any of the details are missing
        if not all([cinema, film, date, show_time, ticket_type, ticket_count]):
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        
        #get the current policy's max days for booking
        max_days_for_booking = self.app.session.query(Policy).first().max_days_for_booking

        #convert the selected date to datetime format
        try:
            date = datetime.strptime(date, "%m/%d/%y")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format.")
            return

        #check if the selected date is more than max_days_for_booking days ahead
        max_date = datetime.now() + timedelta(days=max_days_for_booking)

        if date > max_date:
            messagebox.showerror("Error", f"You cannot book more than {max_days_for_booking} days in advance.")
            return

        #get the selected showing's object from the show_time dict
        showing_obj = self.show_time_dict.get(show_time, None)

        #if all details are valid, proceed to payment
        self.app.show_page(PaymentPage, showing_obj=showing_obj, ticket_type=ticket_type, total_price=self.total_price, ticket_count=ticket_count)

