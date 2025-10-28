#view listings page
    
#import here
import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
from add_listing import AddListingPage
from update_listing import UpdateListingPage
from models import Film

class ViewListingsPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#004466")
        self.app = app
        self.user = self.app.user
        self.app.canvas.configure(bg="#004466")

        self.start_date = datetime.today().date()

        #frontend
        tk.Label(self, text="Listings", font=("Arial", 20), bg="#004466", fg="white").pack(pady=10)

        #get user's cinema
        user_cinema = self.user.cinema

        #get user's role
        self.user_role = self.user.role.title

        user_frame = tk.Frame(self, bg="#004466")
        user_frame.place(x=1000, y=20)

        #display user's cinema, name and role
        tk.Label(user_frame, text=f"Horizon Cinemas {user_cinema.neighbourhood} {user_cinema.city.name}", font=("Arial", 12), bg="#004466", fg="white").pack(pady=10)
        tk.Label(user_frame, text=f"{self.user.name} [{self.user_role}]", font=("Arial", 12), bg="#004466", fg="white").pack(pady=10)

        #filters form
        tk.Label(self, text="Filters", font=("Arial", 14), bg="#004466", fg="white").pack(pady=10)

        filter_frame = tk.Frame(self, bg="#004466")
        filter_frame.pack()

        tk.Label(filter_frame, text="Airing On:", font=("Arial", 12), bg="#004466", fg="white").pack(side="left", padx=5)
        self.date_var = tk.StringVar(value="")
        self.date_entry = DateEntry(filter_frame, font=("Arial", 12), date_pattern='dd/MM/yy', textvariable=self.date_var, state="readonly")
        self.date_var.set("")
        self.date_entry.pack(side="left", padx=5)
        tk.Button(filter_frame, text="Clear Date", command=lambda: self.date_var.set(""), font=("Arial", 12)).pack(side="left", padx=5)

        tk.Label(filter_frame, text="Age Rating:", font=("Arial", 12), bg="#004466", fg="white").pack(side="left", padx=5)
        age_rating_options = ["All", "U", "PG", "12A", "12", "15", "18", "R18"]
        self.ar_selected_option = tk.StringVar()
        self.ar_selected_option.set(age_rating_options[0])
        self.age_rating_dropdown = tk.OptionMenu(filter_frame, self.ar_selected_option, *age_rating_options)
        self.age_rating_dropdown.pack(side="left", padx=5)

        tk.Label(filter_frame, text="Sort By:", font=("Arial", 12), bg="#004466", fg="white").pack(side="left", padx=5)
        sort_options = ["Default", "IMDb Score: High to Low", "IMDb Score: Low to High", "Release Year: Newest to Oldest", "Release Year: Oldest to Newest", "Duration: Shortest to Longest", "Duration: Longest to Shortest"]
        self.sort_selected_option = tk.StringVar()
        self.sort_selected_option.set(sort_options[0])
        self.sort_by_dropdown = tk.OptionMenu(filter_frame, self.sort_selected_option, *sort_options)
        self.sort_by_dropdown.pack(side="left", padx=5)

        tk.Button(filter_frame, text="Apply Filters", font=("Arial", 12), command=self.apply_filters).pack(pady=10)

        #if the user isn't booking staff (i.e. is admin/manager) allow them to add new listings
        if self.user_role.lower() != "booking staff":
            #add new listing button
            tk.Button(self, text="Add a New Listing", font=("Arial", 14), command=lambda: self.app.show_page(AddListingPage)).pack(pady=10,padx=10)

        #date navigation
        nav_frame = tk.Frame(self, bg="#004466")
        nav_frame.pack()

        tk.Button(nav_frame, text="← Prev Week", command=self.prev_week, font=("Arial", 12)).pack(side="left", padx=5)
        self.week_label = tk.Label(nav_frame, text="", font=("Arial", 12), bg="#004466", fg="white")
        self.week_label.pack(side="left", padx=5)
        tk.Button(nav_frame, text="Next Week →", command=self.next_week, font=("Arial", 12)).pack(side="left", padx=5)

        #listings
        self.listings_frame = tk.Frame(self, bg="#004466")
        self.listings_frame.pack(fill="both", expand=True)

        self.display_listings()
            
        #import here to avoid circular import error
        from main_menu import MainMenuPage
        tk.Button(self, text="Back", font=("Arial", 14), command=lambda: self.app.show_page(MainMenuPage)).place(x=20, y=20)

        self.pack(fill="both", expand=True)
    
    #displays listings (filtered_listings init set to None and then when the user applies filters it'll be set to the filtered listings)
    def display_listings(self, filtered_listings=None):
        #clear previous listings before displaying new ones
        for widget in self.listings_frame.winfo_children():
            widget.destroy()

        #listings list (i.e. list of films and their showing times)
        #if filters haven't been applied then show all listings in their default order
        if filtered_listings == None:
            film_listings = self.app.session.query(Film).all()
        #if filters have been applied then show the filtered listings in the set order
        else:
            film_listings = filtered_listings

        #weekly navigation header
        days = [(self.start_date + timedelta(days=i)).strftime('%d %b') for i in range(7)]

        #frame for the header (date row)
        header_frame = tk.Frame(self.listings_frame, bg="#004466")
        header_frame.pack(fill="both", expand=True)

        #add date labels in a row
        for day in range(7):
            tk.Label(header_frame, text=days[day], font=("Arial", 12, "bold"), bg="#004466", fg="white", width=18, relief="ridge").grid(row=0, column=day, padx=2, pady=5)

        #display details of each listing
        for film in film_listings:
            film_frame = tk.Frame(self.listings_frame, bg="#004466", bd=2, relief="solid")
            film_frame.pack(fill="x", expand=True, pady=5, padx=10)

            #film details
            tk.Label(film_frame, text=f"{film.name} ({film.release_year}) | {film.age_rating} IMDb: {film.imdb}",
                    font=("Arial", 12), bg="#004466", fg="white").pack(anchor="w", pady=5)
            tk.Label(film_frame, text=f"{film.duration} mins | {', '.join([genrefilm.genre.name for genrefilm in film.genrefilms])}",
                    font=("Arial", 10), bg="#004466", fg="white").pack(anchor="w")
            tk.Label(film_frame, text=film.description, font=("Arial", 10), bg="#004466", fg="white").pack(anchor="w")
            tk.Label(film_frame, text=f"Starring: {', '.join([actorfilm.actor.name for actorfilm in film.actorfilms])}",
                    font=("Arial", 10), bg="#004466", fg="white").pack(anchor="w")

            #weekly schedule display
            schedule_frame = tk.Frame(film_frame, bg="#004466")
            schedule_frame.pack()

            #display showtimes aligned with dates above
            for day in range(7):
                day_date = self.start_date + timedelta(days=day)
                showings = [f"Screen {s.screen.screen_id}: {s.start_time.strftime('%H:%M')}-{s.end_time.strftime('%H:%M')}"
                            for s in film.showings if s.start_time.date() == day_date]
                text = "\n".join(showings) if showings else "No Showings"
                tk.Label(schedule_frame, text=text, font=("Arial", 10), bg="#004466", fg="white", width=18, relief="ridge").grid(row=0, column=day, padx=2, pady=2)

            #if the user isn't booking staff (i.e. is admin/manager) allow them to update and delete listings
            if self.user_role.lower() != "booking staff":
                button_frame = tk.Frame(film_frame, bg="#004466")
                button_frame.pack(pady=5)
                tk.Button(button_frame, text="Update Listing", font=("Arial", 12), command=lambda f=film: self.app.show_page(UpdateListingPage, film=f)).pack(side="left", padx=5)
                tk.Button(button_frame, text="Delete Listing", font=("Arial", 12), command=lambda f=film: self.delete_listing(f)).pack(side="left", padx=5)


    #function to return filtered listings
    def apply_filters(self):
        #get applied filter options
        #get date_var instead of date_entry -> date_var is the value shown on screen, date_entry is the actual value -> date_entry set to current date by default whereas date_var set to "" until the user selects an option 
        selected_date = self.date_var.get().strip()
        selected_age = self.ar_selected_option.get()
        selected_sort = self.sort_selected_option.get()

        films = self.app.session.query(Film).all()

        #if the user has selected a date then get all films with a showing on the selected date
        if selected_date:
            selected_date_obj = datetime.strptime(selected_date, '%d/%m/%y').date()
            films = [film for film in films if any(showing.start_time.date() == selected_date_obj for showing in film.showings)]

        #if the user has selected an age rating then select films with the selected age rating
        if selected_age != "All":
            films = [film for film in films if film.age_rating == selected_age]

        #if the user has selected an order then sort the list in that order
        if selected_sort == "IMDb Score: High to Low":
            films.sort(key=lambda x: x.imdb, reverse=True)
        elif selected_sort == "IMDb Score: Low to High":
            films.sort(key=lambda x: x.imdb)
        elif selected_sort == "Release Year: Newest to Oldest":
            films.sort(key=lambda x: x.release_year, reverse=True)
        elif selected_sort == "Release Year: Oldest to Newest":
            films.sort(key=lambda x: x.release_year)
        elif selected_sort == "Duration: Shortest to Longest":
            films.sort(key=lambda x: x.duration)
        elif selected_sort == "Duration: Longest to Shortest":
            films.sort(key=lambda x: x.duration, reverse=True)

        self.display_listings(films)

    #function to delete a listing (film parameter passed in through lambda func above)
    def delete_listing(self, film):
        #ask the user to confirm their choice
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to remove the following listing: '{film.name} ({film.release_year})'? All showings of this listing will be deleted and related bookings will be cancelled.")
        #if the user selects yes then cancel all related bookings and remove the listing (film, genrefilms, actorfilms, showings)
        if confirm:
            try:
                #cancel bookings related to the listing
                for showing in film.showings:
                    for booking in showing.bookings:
                        booking.cancelled = True
                        booking.refund_amount = booking.booking_cost #100% refund

                #remove film from the database (and therefore related genrefilms, actorfilms and showings through cascading)
                self.app.session.delete(film)
                self.app.session.commit()
                messagebox.showinfo("Success", f"'{film.name}' has been deleted successfully!")

                #refresh the page
                self.app.show_page(ViewListingsPage)

            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while deleting the listing. Please try again.")
    
    #go back one week
    def prev_week(self):
        #subtract 7 days from the start date
        self.start_date -= timedelta(days=7)
        #reapply filters and show listings
        self.apply_filters()
    
    #go forward one week
    def next_week(self):
        #add 7 days to the start date
        self.start_date += timedelta(days=7)
        #reapply filters and show listings
        self.apply_filters()


