#generate reports page

#import here
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
from sqlalchemy.sql import func
from models import Film, Booking, Cinema, Staff, Showing, Screen, City
from sqlalchemy import case, asc, desc, and_
from tkcalendar import DateEntry
from PIL import Image, ImageTk


class GenerateReportsPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.session = self.app.session
        self.configure(bg="white", padx=130, pady=200)
        
        # Open the image and resize it
        image = Image.open("img3.jpg")
        image = image.resize((600, 400))

        # Convert image to Tkinter-compatible format
        self.photo = ImageTk.PhotoImage(image)

        # Create a label with the image
        image_label = tk.Label(self, image=self.photo)

        # Use .pack() to place the image on the right side
        image_label.pack( side="right",anchor="ne",padx=50, pady=0)
        
         # Create a frame to hold the text section (background color for text area)
        text_frame = tk.Frame(self,bg="white")  # Background color for the text section
        text_frame.place( x=0,y=0,relwidth=0.25, relheight=1)  # Fill the entire area


        #frontend
        tk.Label(self, text="Generate Reports", font=("Arial", 30)).pack(pady=30)

        #create frame for all the filters
        filter_frame = tk.Frame(self,bg="white")
        filter_frame.pack(pady=5)

        #REPORT TYPE
        tk.Label(filter_frame, text="Report Type:", font=("Arial", 12)).pack(side="left",padx=5)
        self.report_var = tk.StringVar()
        reports = ["Number of Bookings Per Film", "Gross Revenue Per Cinema", "Net Revenue Per Cinema", "Gross Revenue Per Film", "Net Revenue Per Film", "Number of Bookings Made Per Staff Member"]
        self.report_dropdown = tk.OptionMenu(filter_frame, self.report_var, *reports)
        self.report_var.set(reports[0])
        self.report_dropdown.pack(side="left", padx=5)

        #SORT BY
        tk.Label(filter_frame, text="Sort By:", font=("Arial", 12)).pack(side="left", padx=5)
        self.sort_var = tk.StringVar()
        sort_options = ["Descending", "Ascending"]
        self.sort_dropdown = tk.OptionMenu(filter_frame, self.sort_var, *sort_options)
        self.sort_var.set(sort_options[0])
        self.sort_dropdown.pack(side="left", padx=5)

        #DATE RANGE
        tk.Label(filter_frame, text="Date Range:", font=("Arial", 12)).pack(side="left", padx=5)
        self.date_range_var = tk.StringVar(value="All Time")
        self.date_range_dropdown = tk.OptionMenu(filter_frame, self.date_range_var, "All Time", "Last 7 Days", "Last 30 Days", "This Year", "Custom")
        self.date_range_dropdown.pack(side="left", padx=5)

        #bind an event to date_range so that if the user selects custom then the custom date entry fields appear
        self.date_range_var.trace_add("write", lambda *args: self.custom_option(filter_frame))
        
        #import here to avoid circular import error
        from main_menu import MainMenuPage
        tk.Button(self, text="Back", font=("Arial", 14), command=lambda: self.app.show_page(MainMenuPage)).pack(padx=10,side="left")

        #GENERATE REPORT BUTTON
        tk.Button(self, text="Generate Report", font=("Arial", 14), command=self.generate_report).pack(padx=5,side="left")

        #create frame for the report generated
        self.report_frame = tk.Frame(self,bg="white")
        self.report_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=30)
        
    #if the user selects custom date range then show the custom date entry fields
    def custom_option(self, parent_frame):
        #if the date range selected is custom then allow user to enter their own range
        if self.date_range_var.get() == "Custom":
            #start date
            self.from_label = tk.Label(parent_frame, text="From:", font=("Arial", 12))
            self.from_label.pack(side="left", padx=5)
            self.start_date_var = tk.StringVar(value="")
            self.start_date_entry = DateEntry(parent_frame, font=("Arial", 12), date_pattern='dd/MM/yy', textvariable=self.start_date_var, state="readonly")
            self.start_date_var.set("")
            self.start_date_entry.pack(side="left", padx=5)
            #end date
            self.to_label = tk.Label(parent_frame, text="to:", font=("Arial", 12))
            self.to_label.pack(side="left", padx=5)
            self.end_date_var = tk.StringVar(value="")
            self.end_date_entry = DateEntry(parent_frame, font=("Arial", 12), date_pattern='dd/MM/yy', textvariable=self.end_date_var, state="readonly")
            self.end_date_var.set("")
            self.end_date_entry.pack(side="left", padx=5)
        #otherwise remove the custom date entry fields and labels if they exist (i.e. if they switch after picking custom)
        else:
            if hasattr(self, 'from_label'):
                self.from_label.destroy()

            if hasattr(self, 'to_label'):
                self.to_label.destroy()

            for widget in parent_frame.winfo_children():
                if isinstance(widget, DateEntry):
                    widget.destroy()

    #get the start and end dates selected to filter with
    def get_date_filter(self):
        #get the current date
        today = datetime.today()
        #get the selected date range
        date_range = self.date_range_var.get()

        #if the user selects last 7 days
        if date_range == "Last 7 Days":
            #then return the start date as (today minus 7 days) and the end date as today
            return today - timedelta(days=7), today
        #if the user selects last 30 days
        elif date_range == "Last 30 Days":
            #then return the start date as (today minus 30 days) and the end date as today
            return today - timedelta(days=30), today
        #if the user selects this year
        elif date_range == "This Year":
            #then return the start date as the first day of the year and the end date as today
            return datetime(today.year, 1, 1), today
        #otherwise if the user selects custom
        elif date_range == "Custom":
            #then convert the start and end dates to datetime objects if they are in the correct format
            try:
                start_date = datetime.strptime(self.start_date_entry.get(), "%d/%m/%y")
                end_date = datetime.strptime(self.end_date_entry.get(), "%d/%m/%y")
                return start_date, end_date
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use DD/MM/YY.")
                return None, None
        return None, None

    #generate a report based on the selected options
    def generate_report(self):
        #get the selected report type, sort order and date range
        report_type = self.report_var.get()
        sort_order = self.sort_var.get()
        start_date, end_date = self.get_date_filter()

        #if the user doesn't select a report type don't generate report (default is set so this shouldn't happen)
        if not all([report_type, sort_order]):
            messagebox.showerror("Error", "Please select a report type and sort order")
            return

        #if the user selects custom but enters invalid dates (not in the format) don't generate report
        if self.date_range_var.get() == "Custom" and (not start_date or not end_date):
            return

        #if the custom start date is after the custom end date don't generate report
        if (start_date and end_date) and (start_date > end_date):
            messagebox.showerror("Error", "Invalid date range. Start date must be before end date.")
            return

        #if the start date is in the future don't generate report
        if start_date and start_date > datetime.today():
            messagebox.showerror("Error", "Invalid date range. Start date must be in the past.")
            return 

        #clear the report frame
        for widget in self.report_frame.winfo_children():
            widget.destroy()

        #call the function to generate the report based on selection
        if report_type == "Number of Bookings Per Film":
            self.bookings_report("Film", sort_order, start_date, end_date)
        elif report_type == "Gross Revenue Per Cinema":
            self.gross_revenue_report("Cinema", sort_order, start_date, end_date)
        elif report_type == "Net Revenue Per Cinema":
            self.net_revenue_report("Cinema", sort_order, start_date, end_date)
        elif report_type == "Gross Revenue Per Film":
            self.gross_revenue_report("Film", sort_order, start_date, end_date)
        elif report_type == "Net Revenue Per Film":
            self.net_revenue_report("Film", sort_order, start_date, end_date)
        elif report_type == "Number of Bookings Made Per Staff Member":
            self.bookings_report("Staff Member", sort_order, start_date, end_date)
        else:
            messagebox.showerror("Error", "Please select a valid report")

    #displays report data as a list
    def display_report(self, title, data):
        #REPORT TITLE
        tk.Label(self.report_frame, text=title, font=("Arial", 14)).pack(pady=5)
        #list of report data
        for row in data:
            tk.Label(self.report_frame, text=" - ".join(map(str, row)), font=("Arial", 12)).pack(padx=10)

    #generate report data for number of bookings per entity chosen (film/staff member)
    def bookings_report(self, entity, sort_order, start_date, end_date):
        #if the user hasn't selected All Time then only count bookings between start and end date
        if start_date and end_date:
            #if the report is for films
            if entity == "Film":
                query = self.session.query(
                    func.concat(Film.name, " (", Film.release_year, ")"), #get the film name and release year
                    func.coalesce(func.count(case( #count the number of bookings associated with the film between start and end date
                        (Booking.booking_date.between(start_date, end_date), Booking.booking_id)
                    )), 0)
                ).outerjoin(Showing, Showing.film_id == Film.film_id #join the showing and film tables
                ).outerjoin(Booking, Booking.showing_id == Showing.showing_id #join the booking and showing tables
                ).group_by(Film.name, Film.release_year) #group count by the film name and release year
            #otherwise if it's for staff members
            else:
                query = self.session.query(
                    Staff.name, #get the staff name
                    func.coalesce(func.count(case( #count the number of bookings associated with the staff between start and end date
                        (Booking.booking_date.between(start_date, end_date), Booking.booking_id)
                    )), 0)
                ).outerjoin(Booking, Booking.staff_id == Staff.staff_id #join the booking and staff tables
                ).group_by(Staff.name) #group count by the staff name

            #sorting based on the count of bookings
            #if the user selects descending order then sort by descending count
            if sort_order == "Descending":
                query = query.order_by(func.count(case(
                    (Booking.booking_date.between(start_date, end_date), Booking.booking_id)
                )).desc())
            #otherwise sort by ascending count
            else:
                query = query.order_by(func.count(case(
                    (Booking.booking_date.between(start_date, end_date), Booking.booking_id)
                )).asc())
        #otherwise count all bookings for each film/staff member
        else:
            #if the report is for films
            if entity == "Film":
                #get the film name and release year and count the number of bookings associated with the film
                query = self.session.query(func.concat(Film.name, " (", Film.release_year, ")"), func.coalesce(func.count(Booking.booking_id), 0)
                ).outerjoin(Showing, Showing.film_id == Film.film_id
                ).outerjoin(Booking, Booking.showing_id == Showing.showing_id
                ).group_by(Film.name, Film.release_year)
            #otherwise if it's for staff members
            else:
                #get the staff name and count the number of bookings associated with the staff member
                query = self.session.query(Staff.name, func.coalesce(func.count(Booking.booking_id), 0)
                ).outerjoin(Booking, Booking.staff_id == Staff.staff_id
                ).group_by(Staff.name)

            #sorting based on the count of bookings
            if sort_order == "Descending":
                query = query.order_by(func.count(Booking.booking_id).desc())
            else:
                query = query.order_by(func.count(Booking.booking_id).asc())
        
        #get all the data retreived
        data = query.all()
        #display the data
        self.display_report(f"Number of Bookings Per {entity}:", data)
    
    #generate report data for gross revenue per entity chosen (cinema/film)
    def gross_revenue_report(self, entity, sort_order, start_date, end_date):
        #if the user hasn't selected All Time then only count booking costs between start and end date
        if start_date and end_date:
            #if the report is for cinemas
            if entity == "Cinema":
                query = self.session.query(
                    func.concat(Cinema.neighbourhood, " ", City.name), #get the cinema neighbourhood and city name
                    func.coalesce(func.sum(case( #sum the booking costs associated with the cinema between start and end date
                        (Booking.booking_date.between(start_date, end_date), Booking.booking_cost)
                    )), 0)
                ).outerjoin(Screen, Screen.cinema_id == Cinema.cinema_id #join the screen and cinema tables
                ).outerjoin(Showing, Showing.screen_id == Screen.screen_id #join the showing and screen tables
                ).outerjoin(Booking, Booking.showing_id == Showing.showing_id #join the booking and showing tables
                ).join(City, Cinema.city_id == City.city_id #join the cinema and city tables to access the cinema's city name
                ).group_by(Cinema.neighbourhood, City.name) #group sum by the cinema neighbourhood and city name
            #otherwise if it's for films
            else:
                query = self.session.query(
                    func.concat(Film.name, " (", Film.release_year, ")"), #get the film name and release year
                    func.coalesce(func.sum(case( #sum the booking costs associated with the film between start and end date
                        (Booking.booking_date.between(start_date, end_date), Booking.booking_cost)
                    )), 0)
                ).outerjoin(Showing, Showing.film_id == Film.film_id #join the showing and film tables
                ).outerjoin(Booking, Booking.showing_id == Showing.showing_id #join the booking and showing tables
                ).group_by(Film.name, Film.release_year) #group sum by the film name

            #sorting based on the sum of booking costs
            #if the user selects descending order then sort by descending sum
            if sort_order == "Descending":
                query = query.order_by(func.sum(case(
                    (Booking.booking_date.between(start_date, end_date), Booking.booking_cost)
                )).desc())
            #otherwise sort by ascending sum
            else:
                query = query.order_by(func.sum(case(
                    (Booking.booking_date.between(start_date, end_date), Booking.booking_cost)
                )).asc())
        #otherwise sum all booking costs for each cinema
        else:
            #if the report is for cinemas
            if entity == "Cinema":
                #get the cinema neighbourhood and city name and sum the booking costs associated with the cinema
                query = self.session.query(
                    func.concat(Cinema.neighbourhood, " ", City.name),
                    func.coalesce(func.sum(Booking.booking_cost), 0)
                ).outerjoin(Screen, Screen.cinema_id == Cinema.cinema_id
                ).outerjoin(Showing, Showing.screen_id == Screen.screen_id
                ).outerjoin(Booking, Booking.showing_id == Showing.showing_id
                ).join(City, Cinema.city_id == City.city_id
                ).group_by(Cinema.neighbourhood, City.name)
            #otherwise if it's for films
            else:
                #get the film name and release year and sum the booking costs associated with the film
                query = self.session.query(func.concat(Film.name, " (", Film.release_year, ")"), func.coalesce(func.sum(Booking.booking_cost), 0)
                ).outerjoin(Showing, Showing.film_id == Film.film_id
                ).outerjoin(Booking, Booking.showing_id == Showing.showing_id
                ).group_by(Film.name, Film.release_year)

            #sorting based on the sum of booking costs
            if sort_order == "Descending":
                query = query.order_by(func.sum(Booking.booking_cost).desc())
            else:
                query = query.order_by(func.sum(Booking.booking_cost).asc())

        #get all the data retreived
        data = query.all()
        #display the data
        self.display_report(f"Gross Revenue Per {entity}:", data)

    #generate report data for net revenue per entity chosen (cinema/film)
    def net_revenue_report(self, entity, sort_order, start_date, end_date):
        #if the user hasn't selected All Time then only count booking costs/refund amounts between start and end date
        if start_date and end_date:
            #calculate the total revenue (sum of booking_costs) for bookings between start and end date
            total_revenue = func.coalesce(
                func.sum(
                    case( #if the booking is between start-end date then sum the booking cost
                        (Booking.booking_date.between(start_date, end_date), Booking.booking_cost),
                        else_=0
                    )
                ), 0
            )
            #calculate the total refunds (sum of refund_amounts) for bookings between start and end date
            total_refunds = func.coalesce(
                func.sum(
                    case( #if the booking is between start-end date and has been cancelled then sum the refund amount
                        (and_(Booking.booking_date.between(start_date, end_date), Booking.cancelled == True), Booking.refund_amount),
                        else_=0
                    )
                ), 0
            )
            #calculate the net revenue (total revenue - total refunds)
            net_revenue = (total_revenue - total_refunds).label("net_revenue")
        #otherwise sum the net_revenue over all bookings
        else:
            #calculate the total revenue for all bookings
            total_revenue = func.coalesce(func.sum(Booking.booking_cost), 0)
            #calculate the total refunds for cancelled bookings without filtering out any dates
            total_refunds = func.coalesce(
                func.sum(
                    case(
                        (Booking.cancelled == True, Booking.refund_amount),
                        else_=0
                    )
                ), 0
            )
            #calculate the net revenue (total revenue - total refunds)
            net_revenue = (total_revenue - total_refunds).label("net_revenue")
        
        #if the report is for cinemas
        if entity == "Cinema":
            query = self.session.query(
                func.concat(Cinema.neighbourhood, " ", City.name), #get the cinema neighbourhood and city name
                net_revenue #get the net revenue
            ).outerjoin(Screen, Screen.cinema_id == Cinema.cinema_id #join the screen and cinema tables
            ).outerjoin(Showing, Showing.screen_id == Screen.screen_id #join the showing and screen tables
            ).outerjoin(Booking, Booking.showing_id == Showing.showing_id #join the booking and showing tables
            ).join(City, Cinema.city_id == City.city_id #join the cinema and city tables to access the cinema's city name
            ).group_by(Cinema.neighbourhood, City.name) #group sum by the cinema neighbourhood and city name
        #otherwise if it's for films
        else:
            query = self.session.query(
                func.concat(Film.name, " (", Film.release_year, ")"), #get the film name and release year
                net_revenue #get the net revenue
            ).outerjoin(Showing, Showing.film_id == Film.film_id #join the showing and film tables
            ).outerjoin(Booking, Booking.showing_id == Showing.showing_id #join the booking and showing tables
            ).group_by(Film.name, Film.release_year) #group sum by the film name and release year

        #sorting based on the net revenue
        #if the user selects descending order then sort by descending net revenue
        if sort_order == "Descending":
            query = query.order_by(desc("net_revenue"))
        #otherwise sort by ascending net revenue
        else:
            query = query.order_by(asc("net_revenue"))

        #get all the data
        data = query.all()
        #display the data
        self.display_report(f"Net Revenue Per {entity}:", data)



