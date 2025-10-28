#add listing page

#import here
import tkinter as tk
from tkinter import messagebox, StringVar
from tkcalendar import DateEntry
from utils import is_valid_film_name, is_valid_description, is_valid_imdb, is_valid_duration, is_valid_release_year, is_valid_name, is_valid_genre, is_valid_datetime
from sqlalchemy import text, cast, Date
from models import Showing, Film, Actor, Genre, ActorFilm, GenreFilm, Policy
import datetime
from datetime import datetime, time

class AddListingPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.user = self.app.user
        self.configure(bg="#004466", padx=200, pady=20)

        #lists to store values of added entries
        self.actor_entries = []
        self.genre_entries = []
        self.showing_entries = []

        #grid layout for frontend
        self.grid_row = 0

        #frontend
        tk.Label(self, text="Add a New Listing", font=("Arial", 20), bg="#004466", fg="white").grid(row=self.grid_row, column=0, columnspan=2, pady=10)
        self.grid_row += 1

        tk.Label(self, text="Film Name:", font=("Arial", 14), bg="#004466", fg="white").grid(row=self.grid_row, column=0, sticky="w", pady=10)
        self.name_entry = tk.Entry(self, font=("Arial", 14),relief="solid")
        self.name_entry.grid(row=self.grid_row, column=1, pady=5)
        self.grid_row += 1

        tk.Label(self, text="Description:", font=("Arial", 14), bg="#004466", fg="white").grid(row=self.grid_row, column=0, sticky="w", pady=10)
        self.description_entry = tk.Entry(self, font=("Arial", 14),relief="solid")
        self.description_entry.grid(row=self.grid_row, column=1, pady=5)
        self.grid_row += 1

        tk.Label(self, text="Age Rating:", font=("Arial", 14), bg="#004466", fg="white").grid(row=self.grid_row, column=0, sticky="w", pady=10)
        age_rating_options = ["U", "PG", "12A", "12", "15", "18", "R18"] #BBFC ratings
        self.ar_selected_option = tk.StringVar()
        self.ar_selected_option.set(age_rating_options[0])
        self.age_rating_dropdown = tk.OptionMenu(self, self.ar_selected_option, *age_rating_options)
        self.age_rating_dropdown.grid(row=self.grid_row, column=1, pady=5)
        self.grid_row += 1

        tk.Label(self, text="IMDb Score:", font=("Arial", 14), bg="#004466", fg="white").grid(row=self.grid_row, column=0, sticky="w", pady=10)
        self.imdb_entry = tk.Entry(self, font=("Arial", 14),relief="solid")
        self.imdb_entry.grid(row=self.grid_row, column=1, pady=5)
        self.grid_row += 1

        tk.Label(self, text="Duration (minutes):", font=("Arial", 14), bg="#004466", fg="white").grid(row=self.grid_row, column=0, sticky="w", pady=10)
        self.duration_entry = tk.Entry(self, font=("Arial", 14),relief="solid")
        self.duration_entry.grid(row=self.grid_row, column=1, pady=5)
        self.grid_row += 1

        tk.Label(self, text="Release Year:", font=("Arial", 14), bg="#004466", fg="white").grid(row=self.grid_row, column=0, sticky="w", pady=10)
        self.release_year_entry = tk.Entry(self, font=("Arial", 14),relief="solid")
        self.release_year_entry.grid(row=self.grid_row, column=1, pady=5)
        self.grid_row += 1

        #actors section
        tk.Label(self, text="Main Cast:", font=("Arial", 14), bg="#004466", fg="white").grid(row=self.grid_row, column=0, sticky="w", pady=10)
        self.grid_row += 1
        self.actor_frame = tk.Frame(self, bg="#004466")
        self.actor_frame.grid(row=self.grid_row, column=0, columnspan=2, sticky="w", pady=5)
        self.grid_row += 1
        self.add_actor_section()

        #genres section
        tk.Label(self, text="Genres:", font=("Arial", 14), bg="#004466", fg="white").grid(row=self.grid_row, column=0, sticky="w", pady=10)
        self.grid_row += 1
        self.genre_frame = tk.Frame(self, bg="#004466")
        self.genre_frame.grid(row=self.grid_row, column=0, columnspan=2, sticky="w", pady=5)
        self.grid_row += 1
        self.add_genre_section()

        #showings section
        tk.Label(self, text="Showings:", font=("Arial", 14), bg="#004466", fg="white").grid(row=self.grid_row, column=0, sticky="w", pady=10)
        self.grid_row += 1
        self.showing_frame = tk.Frame(self, bg="#004466")
        self.showing_frame.grid(row=self.grid_row, column=0, columnspan=2, sticky="w", pady=5)
        self.grid_row += 1
        self.add_showing_section()

        tk.Button(self, text="Add Listing", font=("Arial", 14), command=self.add_listing).grid(row=self.grid_row, column=1, sticky="w", pady=(10, 200))
        self.grid_row += 1

        from view_listings import ViewListingsPage
        tk.Button(self, text="Back", font=("Arial", 14), command=lambda: self.app.show_page(ViewListingsPage)).place(x=0, y=0)
    
    def add_actor_section(self):
        #create a frame for the first (default) entry and button
        self.actor_first_row = tk.Frame(self.actor_frame, bg="#004466")
        self.actor_first_row.pack(side="top", padx=5)

        #create the "Add Another Actor" button and place it to the right of the first entry
        self.add_actor_button = tk.Button(self.actor_first_row, text="Add Another Actor", font=("Arial", 14), command=self.add_actor_entry)
        self.add_actor_button.pack(side="right", padx=5)

        #add the first entry and place it to the left of the button
        self.first_actor_entry = tk.Entry(self.actor_first_row, font=("Arial", 14))
        self.first_actor_entry.pack(side="left")

        #store the first entry in a list to access values of each entry later
        self.actor_entries.append(self.first_actor_entry)

        #create a frame for additional entries
        self.actor_entries_frame = tk.Frame(self.actor_frame, bg="#004466")
        self.actor_entries_frame.pack(side="left", padx=5)

    def add_actor_entry(self):
        #create a new entry and place it below the first entry
        entry = tk.Entry(self.actor_entries_frame, font=("Arial", 14))
        entry.pack(side="top", pady=5)
        self.actor_entries.append(entry)

    def add_genre_section(self):
        #create a frame for the first (default) entry and button
        self.genre_first_row = tk.Frame(self.genre_frame, bg="#004466")
        self.genre_first_row.pack(side="top", padx=5)

        #create the "Add Another Genre" button and place it to the right of the first entry
        self.add_genre_button = tk.Button(self.genre_first_row, text="Add Another Genre", font=("Arial", 14), command=self.add_genre_entry)
        self.add_genre_button.pack(side="right", padx=5)

        #add the first entry and place it to the left of the button
        self.first_genre_entry = tk.Entry(self.genre_first_row, font=("Arial", 14))
        self.first_genre_entry.pack(side="left")

        #store the first entry in a list to access values of each entry later
        self.genre_entries.append(self.first_genre_entry)

        #create a frame for additional entries
        self.genre_entries_frame = tk.Frame(self.genre_frame, bg="#004466")
        self.genre_entries_frame.pack(side="left", padx=5)

    def add_genre_entry(self):
        #create a new entry and place it below the first entry
        entry = tk.Entry(self.genre_entries_frame, font=("Arial", 14))
        entry.pack(side="top", pady=5)
        self.genre_entries.append(entry)

    def add_showing_section(self):
        #create a frame for the first (default) entry and button
        self.showing_first_row = tk.Frame(self.showing_frame, bg="#004466")
        self.showing_first_row.pack(side="top", padx=5)

        #create the "Add Another Showing" button and place it to the right of the first entry
        self.add_showing_button = tk.Button(self.showing_first_row, text="Add Another Showing", font=("Arial", 14), command=self.add_showing_entry)
        self.add_showing_button.pack(side="right", padx=5,pady=10)

        #add the first row of widgets: Date picker, Time picker, and Screen dropdown
        self.add_showing_row(self.showing_first_row)

        #create a frame for additional entries
        self.showing_entries_frame = tk.Frame(self.showing_frame, bg="#004466")
        self.showing_entries_frame.pack(side="left", padx=5)
    
    #function that updates screen options everytime a date/time is selected
    def update_screen_options(self, date_entry, screen_selected_option, screen_dropdown, start_hour_var, start_minute_var, start_period_var, end_hour_var, end_minute_var, end_period_var):
        #get the selected date from the DateEntry
        selected_date = date_entry.get_date()

        #convert start and end time variables into datetime objects to be used in the query
        start_time = self._convert_to_datetime(selected_date, start_hour_var, start_minute_var, start_period_var)
        end_time = self._convert_to_datetime(selected_date, end_hour_var, end_minute_var, end_period_var)
        
        #print(f"start_time type: {type(start_time)}, value: {start_time}")
        #print(f"end_time type: {type(end_time)}, value: {end_time}")

        #get max_shows_per_day from policy tables
        policy = self.app.session.query(Policy).first()
        self.max_shows_per_day = policy.max_shows_per_day

        #query the database for screens (for any cinema) with less than max showings on the selected date (and that doesn't have any overlapping showings)
        raw_query = text("""
            SELECT DISTINCT 
                screen.screen_id,
                CASE 
                    WHEN (SELECT COUNT(*) FROM showing s 
                        WHERE s.screen_id = screen.screen_id 
                        AND DATE(s.start_time) = :date_1) < 3
                    THEN 
                        CASE 
                            WHEN NOT EXISTS (
                                SELECT 1 FROM showing s
                                WHERE s.screen_id = screen.screen_id 
                                AND DATE(s.start_time) = :date_1 
                                AND s.end_time > :start_time_1
                                AND s.start_time < :end_time_1
                            )
                            THEN 'Select'
                            ELSE 'Exclude'
                        END
                    ELSE 'Exclude'
                END AS selection_status
            FROM 
                screen
            LEFT OUTER JOIN 
                showing ON screen.screen_id = showing.screen_id
            WHERE 
                screen.available = TRUE
                AND (
                    showing.start_time IS NULL 
                    OR showing.end_time <= :start_time_1 
                    OR showing.start_time >= :end_time_1
                )
            HAVING 
                selection_status = 'Select'
        """)

        result = self.app.session.execute(raw_query, {
            'date_1': selected_date,
            'start_time_1': start_time,
            'end_time_1': end_time,
            'count_1': self.max_shows_per_day
        })
        
        screens_with_less_than_max_showings = result.fetchall()

        #print(screens_with_less_than_max_showings)

        #set options to appear in the dropdown
        screen_options = [f"Screen {screen.screen_id}" for screen in screens_with_less_than_max_showings]

        #clear and update the dropdown menu with the new options
        menu = screen_dropdown["menu"]
        menu.delete(0, "end")
        for option in screen_options:
            menu.add_command(label=option, command=lambda value=option: screen_selected_option.set(value))

        #set the first option as the default (if available)
        if screen_options:
            screen_selected_option.set(screen_options[0])
        else:
            screen_selected_option.set("No Screens Available")

    def _convert_to_datetime(self, selected_date, hour_var, minute_var, period_var):
        #convert time variables to a datetime object
        hour = int(hour_var.get())
        minute = int(minute_var.get())
        if period_var.get() == "PM" and hour != 12:
            hour += 12
        elif period_var.get() == "AM" and hour == 12:
            hour = 0
        return datetime.combine(selected_date, time(hour, minute))

    def add_showing_row(self, parent_frame):
        #date picker
        date_label = tk.Label(parent_frame, text="Date:", font=("Arial", 14), bg="#004466", fg="white")
        date_label.pack(side="left", padx=5)
        date_entry = DateEntry(parent_frame, font=("Arial", 14), date_pattern='dd/MM/yy')
        date_entry.pack(side="left", padx=5)

        #start time picker
        start_time_label = tk.Label(parent_frame, text="Start Time:", font=("Arial", 14), bg="#004466", fg="white")
        start_time_label.pack(side="left", padx=5)
        start_time_picker = tk.Frame(parent_frame)

        start_hour_var = StringVar(value="12")
        start_minute_var = StringVar(value="00")
        start_period_var = StringVar(value="AM")

        hours = [f"{i:02}" for i in range(1, 13)]
        minutes = [f"{i:02}" for i in range(60)]
        periods = ["AM", "PM"]

        tk.Spinbox(start_time_picker, values=hours, textvariable=start_hour_var, wrap=True, width=3).pack(side=tk.LEFT)
        tk.Spinbox(start_time_picker, values=minutes, textvariable=start_minute_var, wrap=True, width=3).pack(side=tk.LEFT)
        tk.Spinbox(start_time_picker, values=periods, textvariable=start_period_var, wrap=True, width=3).pack(side=tk.LEFT)
        start_time_picker.pack(side="left", padx=5)

        #end time picker
        end_time_label = tk.Label(parent_frame, text="End Time:", font=("Arial", 14), bg="#004466", fg="white")
        end_time_label.pack(side="left", padx=5)
        end_time_picker = tk.Frame(parent_frame)

        end_hour_var = StringVar(value="12")
        end_minute_var = StringVar(value="00")
        end_period_var = StringVar(value="AM")

        tk.Spinbox(end_time_picker, values=hours, textvariable=end_hour_var, wrap=True, width=3).pack(side=tk.LEFT)
        tk.Spinbox(end_time_picker, values=minutes, textvariable=end_minute_var, wrap=True, width=3).pack(side=tk.LEFT)
        tk.Spinbox(end_time_picker, values=periods, textvariable=end_period_var, wrap=True, width=3).pack(side=tk.LEFT)
        end_time_picker.pack(side="left", padx=5)

        #screen dropdown
        screen_label = tk.Label(parent_frame, text="Screen:", font=("Arial", 14), bg="#004466", fg="white")
        screen_label.pack(side="left", padx=5)
        screen_selected_option = tk.StringVar()
        screen_dropdown = tk.OptionMenu(parent_frame, screen_selected_option, [])
        screen_dropdown.pack(side="left", padx=5)

        #initialise screen dropdown options on first load (before changes are made to the date and time variables)
        self.update_screen_options(date_entry, screen_selected_option, screen_dropdown, start_hour_var, start_minute_var, start_period_var, end_hour_var, end_minute_var, end_period_var)

        #bind an event to data_entry so that when a date is selected update_screen_options is called and the screen options are updated
        date_entry.bind("<<DateEntrySelected>>", lambda e: self.update_screen_options(date_entry, screen_selected_option, screen_dropdown, start_hour_var, start_minute_var, start_period_var, end_hour_var, end_minute_var, end_period_var))

        #use the trace_add method to monitor changes in the time variables then call the update_screen_options func to update the screen dropdown
        for var in (start_hour_var, start_minute_var, start_period_var, end_hour_var, end_minute_var, end_period_var):
            var.trace_add("write", lambda *args: self.update_screen_options(date_entry, screen_selected_option, screen_dropdown, start_hour_var, start_minute_var, start_period_var, end_hour_var, end_minute_var, end_period_var))

        #store this row of entries as a tuple in the showing_entries list
        self.showing_entries.append((date_entry, start_time_picker, end_time_picker, screen_selected_option))

    def add_showing_entry(self):
        #create a new row for additional showings
        row_frame = tk.Frame(self.showing_entries_frame, bg="#004466")
        row_frame.pack(side="top", pady=5)

        #add widgets (date picker, time picker, and screen dropdown) to this row
        self.add_showing_row(row_frame)

    #check if two showings overlap
    def is_overlapping(self, showing1, showing2):
        return showing1.start_time < showing2.end_time and showing1.end_time > showing2.start_time #returns True or False
    
    #check if new showings don't overlap with each other or existing showings and if they don't exceed the maximum number of showings per day
    def validate_showings(self, existing_showings, new_showings, max_showings_per_day):
        #group existing and new showings together by screen and day
        showings_by_screen_day = {}
        
        for showing in existing_showings + new_showings:
            key = (showing.screen_id, showing.start_time.date())
            if key not in showings_by_screen_day:
                showings_by_screen_day[key] = []
            showings_by_screen_day[key].append(showing)
        
        #validate each screen/day pair
        for (screen_id, day), showings in showings_by_screen_day.items():
            #check if number of showings exceeds the maximum showings per day
            if len(showings) > max_showings_per_day:
                return (False, f"There can only be a maximum of {max_showings_per_day} showings for Screen {screen_id} on {day}.")
            
            #check for overlapping showings
            for i, showing1 in enumerate(showings):
                for showing2 in showings[i+1:]:
                    if self.is_overlapping(showing1, showing2):
                        return (False, f"Overlapping showings detected on Screen {screen_id} on {day}: "
                                    f"({showing1.start_time} - {showing1.end_time}) "
                                    f"and ({showing2.start_time} - {showing2.end_time}).")
        
        return (True, "All showings validated successfully.")

    def fetch_existing_showings_from_db(self, new_showings):
        #extract all the dates of the new showings
        dates = set([showing.start_time.date() for showing in new_showings])

        #query the database for showings that have the same date as one of the new showings
        existing_showings = self.app.session.query(Showing).filter(cast(Showing.start_time, Date).in_(dates)).all()

        return existing_showings

    def add_listing(self):
        #get form values entered by user .strip() = remove leading/trailing whitespace to avoid issues in validation
        film_name = self.name_entry.get().strip()
        description = self.description_entry.get().strip()
        age_rating = self.ar_selected_option.get().strip()
        imdb_score = self.imdb_entry.get().strip()
        duration = self.duration_entry.get().strip()
        release_year = self.release_year_entry.get().strip()
        actors = [entry.get().strip() for entry in self.actor_entries]
        genres = [entry.get().strip() for entry in self.genre_entries]

        #validation
        #if one of the details is missing then return error message
        if not all([film_name, description, age_rating, imdb_score, duration, release_year]):
            messagebox.showerror("Error", "Please fill in all the details")
            return

        #validate film fields using their respective utility functions
        validators = [
            (is_valid_film_name, film_name, "Error in film name"),
            (is_valid_description, description, "Error in description"),
            (is_valid_imdb, imdb_score, "Error in IMDb score"),
            (is_valid_duration, duration, "Error in duration"),
            (is_valid_release_year, release_year, "Error in release year")
        ]
        
        for validator, value, error_message in validators:
            validation_error = validator(value)
            if validation_error:
                messagebox.showerror("Error", validation_error)
                return
            
        #check if the film already exists (same film name, release year and duration)
        film = self.app.session.query(Film).filter_by(name=film_name, release_year=release_year, duration=duration).first()

        if film:
            messagebox.showerror("Error", "The entered film already exists in the database. If you'd like to update the film listing, please select the Update Listing option in the Listings page instead.")
            return

        #actors validation
        for actor in actors:
            actor_name_error = is_valid_name("Actor", actor)
            if actor_name_error:
                messagebox.showerror("Error", actor_name_error)
                return

        #genres validation
        for genre in genres:
            genre_error = is_valid_genre(genre)
            if genre_error:
                messagebox.showerror("Error", genre_error)
                return

        #showings validation
        new_showings = []
        for showing in self.showing_entries:
            #get all the values inputted from the showing tuple
            date_value = showing[0].get()

            #get the hour, minute and period from the spinboxes for the start and end times
            start_hour = showing[1].children['!spinbox'].get()
            start_minute = showing[1].children['!spinbox2'].get()
            start_period = showing[1].children['!spinbox3'].get()
            start_time_value = f"{start_hour}:{start_minute} {start_period}" #format the time value

            end_hour = showing[2].children['!spinbox'].get()
            end_minute = showing[2].children['!spinbox2'].get()
            end_period = showing[2].children['!spinbox3'].get()
            end_time_value = f"{end_hour}:{end_minute} {end_period}"

            #get the screen selected
            screen_value = showing[3].get()

            #check if date, start time, end time or screen are missing from the showing
            if not all([date_value, start_time_value, end_time_value, screen_value]):
                messagebox.showerror("Error", "Please fill in all showing details.")
                return
            
            #if there are no screens available for some of the showings then return error
            if screen_value == "No Screens Available":
                messagebox.showerror("Error", "There are no screens available for some of your showings. Please try selecting a different date and/or time for those showings.")
                return

            #validate date and times
            date_error = is_valid_datetime(date_value, start_time_value, end_time_value) #see utils.py
            if date_error:
                messagebox.showerror("Error", date_error)
                return

            #create showing objects for each showing so they can be compared with existing showing objects from the database
            showing_obj = Showing(
                start_time=datetime.strptime(f"{date_value} {start_time_value}", "%d/%m/%y %I:%M %p"),
                end_time=datetime.strptime(f"{date_value} {end_time_value}", "%d/%m/%y %I:%M %p"),
                screen_id=int(screen_value.split()[-1]),  #split "Screen" from screen_id
                film_id=None,  #this will be set later when adding the film to the database
            )
            new_showings.append(showing_obj)

        #validate showings with existing ones from the database
        existing_showings = self.fetch_existing_showings_from_db(new_showings)  #get existing showings from the database
        is_valid, validation_message = self.validate_showings(existing_showings, new_showings, self.max_shows_per_day)

        #if any of the showings overlap with each other or existing showings OR adding the new showings exceeds the maximum number of showings per day return an error
        if not is_valid:
            messagebox.showerror("Error", validation_message)
            return

        #if all validations pass, proceed with adding the listing

        #add the film to the database
        new_film = Film(name=film_name, description=description, age_rating=age_rating, imdb=imdb_score, duration=duration, release_year=release_year)
        self.app.session.add(new_film)
        self.app.session.flush() #get film_id without committing yet

        #check if actors already exist in the database
        #loop through all the actors checking one by one if they already exist in the database
        for actor in actors:
            actor_exists = self.app.session.query(Actor).filter(Actor.name.ilike(actor)).first() #case insensitive
            #if the actor doesn't exist add them to the database
            if not actor_exists:
                new_actor = Actor(name=actor)
                self.app.session.add(new_actor)
                self.app.session.flush() #get actor_id without committing yet
            else:
                #otherwise get the actor's record
                new_actor = actor_exists

            #add the relationship to ActorFilm
            new_actor_film = ActorFilm(actor_id=new_actor.actor_id, film_id=new_film.film_id)
            self.app.session.add(new_actor_film)

        #check if genres already exist in the database
        #loop through all the genres checking one by one if they already exist in the database
        for genre in genres:
            genre_exists = self.app.session.query(Genre).filter(Genre.name.ilike(genre)).first() #case insensitive
            #if the genre doesn't exist add it to the database
            if not genre_exists:
                new_genre = Genre(name=genre)
                self.app.session.add(new_genre)
                self.app.session.flush() #get genre_id without committing yet
            else:
                #otherwise get the genre's record
                new_genre = genre_exists
            
            #add the relationship to GenreFilm
            new_genre_film = GenreFilm(genre_id=new_genre.genre_id, film_id=new_film.film_id)
            self.app.session.add(new_genre_film)

        #add the showings to the database
        for showing in new_showings: #new_showings has the Showing objects created when validating but missing film_id
            showing.film_id = new_film.film_id  #set the missing film_id for each showing
            self.app.session.add(showing)

        #commit the changes to the database
        self.app.session.commit()
        #add the showings to the database
        messagebox.showinfo("Success", "Listing added successfully!")

        #redirect back to the View Listings Page
        from view_listings import ViewListingsPage
        self.app.show_page(ViewListingsPage)



