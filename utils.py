#all things validation

#import here
from password_strength import PasswordPolicy
import re
from models import Staff, Seat, SeatPricing, Booking, BookingSeat
import re
from datetime import datetime, timedelta
from decimal import Decimal
from tkcalendar import Calendar

def is_valid_name(model, name):
    #if the name is more than 100 characters long return an error message
    if len(name) > 100 or len(name) < 1:
        return f"{model} name must be between 1 and 100 characters long"
    
    #if the name doesn't match the regex pattern for a full name with optional middle names/initials/double-barreled names, return an error message
    name_pattern = r'^[A-Z](?:[a-z]+|\.)?(?:-[A-Z][a-z]+)? [A-Z](?:[a-z]+|\.)?(?:-[A-Z][a-z]+)?(?: [A-Z](?:[a-z]+|\.)?(?:-[A-Z][a-z]+)?)*$'
    if not re.match(name_pattern, name):
        return f"{model} name must be a correctly capitalised full name"
    
    return None

def is_valid_email(email, session):
    #if the email is more than 320 characters long return an error message
    if len(email) > 320:
        return "Email cannot be more than 320 characters long."
    
    #if the email doesn't match the regex pattern for an email address, return an error message
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return "Please enter a valid email address"
    
    #if the email is not unique return an error message (ilike performs case-insensitive search)
    if session.query(Staff).filter(Staff.email.ilike(email)).first():
        return "The email you're trying to add has already been taken. Please enter a different email address."
    
    return None

#validate passwords entered
def is_valid_password(password1, password2):
    #requirements for valid strong password
    policy = PasswordPolicy.from_names(
        length=8,  # min length: 8
        uppercase=1,  # need min. 1 uppercase letters
        numbers=1,  # need min. 1 digits
        special=1,  # need min. 1 special characters
        nonletters=1,  # need min. 1 non-letter characters (digits, specials, anything)
    )

    #check password is valid length
    if len(password1) > 255:
        return "Password is too long. Password must be less than 256 characters long"
    #check password fits policy requirements
    if len(policy.test(password1)) != 0:
        return "Password is too weak. Please enter a password that is: at least 8 characters long and is made up of at least 1 uppercase, number and special character."
    #check password matches confirmation
    if password1 != password2:
        return "Password and password confirmation do not match! Please try again"
    
    return None

#validate film names
def is_valid_film_name(film_name):
    if len(film_name) > 200:
        return "Film name cannot be more than 200 characters long"
    
    return None

#validate description
def is_valid_description(description):
    if len(description) > 2000:
        return "Description cannot be more than 2000 characters long"
    
    return None

#validate imdb scores
def is_valid_imdb(score):
    #if the score is not in the range 0.0 to 10.0 (and 1 decimal place) return an error message
    if re.match(r"^(10(\.0)?|([0-9](\.\d)?))$", score):
        #convert to decimal so that it can be stored in database
        score = Decimal(score)
        if 0.0 <= score <= 10.0:
            return None

    return "Please enter a valid IMDB score between 0.0 and 10.0"

#validate durations (minutes)
def is_valid_duration(duration):
    try:
        #convert to integer so that it can be stored in database
        duration = int(duration)
        #if duration is negative return an error message
        if duration < 1:
            return "Duration cannot be less than 1 minute"
    #if fails to be converted then duration is invalid
    except ValueError:
        return "Duration must be an integer"
    
    return None

#validate release years
def is_valid_release_year(year):
    try:
        #convert to integer so that it can be stored in database
        year = int(year)
        #get the current year
        current_year = datetime.now().year
        #check within mySQL YEAR range and current year
        if 1901 <= year <= current_year:
            return None
        else:
            return f"Release year must be between 1901 and {current_year}"
    except ValueError:
        return "Release year must be an integer"

#validate genres
def is_valid_genre(genre):
    #no genre shorter than 3 characters and database can't handle more than 50 characters for genre
    if len(genre) > 50 or len(genre) < 3:
        return "Genre name has to be between 3 and 50 characters long"
    
    return None

#validate date and start and end time
def is_valid_datetime(date, start_time, end_time):
    #validate date and time format
    try:
        showing_date_starttime = datetime.strptime(f"{date} {start_time}", "%d/%m/%y %I:%M %p")
        showing_date_endtime = datetime.strptime(f"{date} {end_time}", "%d/%m/%y %I:%M %p")
    except ValueError:
        return "Invalid date or time format. Please use DD/MM/YY and a valid start and end time."
    
    #check if the start time is before 8AM
    if showing_date_starttime.hour < 8:
        return "The start time cannot be before 8AM."
    
    #check if the end time is after 11:59PM
    if showing_date_endtime.hour > 23 and showing_date_endtime.minute > 59:
        return "The end time cannot be after 11:59PM."

    #check if the date and start time is in the future
    if showing_date_starttime <= datetime.now():
        return "The showing date and time must be in the future."

    #check if the start time is before the end time
    if showing_date_starttime >= showing_date_endtime:
        return "The start time must be before the end time."
    return None

#inherits from tkcalendar's Calendar module
class MyCalendar(Calendar):
    def __init__(self, master=None, **kw):
        self._disabled_dates = [] #list of dates to disable
        Calendar.__init__(self, master, **kw) #call parent class constructor

    #function to disable a date
    def disable_date(self, date):
        #add the date to the list of disabled dates
        self._disabled_dates.append(date)
        mi, mj = self._get_day_coords(date) #get the cell coordinates of the date
        if mi is not None:
            self._calendar[mi][mj].state(['disabled']) #disable the date

    #calendar refreshes when user moves between months so dates have to also be disabled in display_calendar (display_calendar called every refresh)
    #override the display_calendar method to disable specific dates
    def _display_calendar(self):
        Calendar._display_calendar(self)
        #loop through the list of disabled dates and update the display accordingly
        for date in self._disabled_dates:
            mi, mj = self._get_day_coords(date) #get the cell coordinates of the date
            if mi is not None:
                self._calendar[mi][mj].state(['disabled']) #disable the date

#validate the number of tickets spinbox
def validate_spinbox(input, max_seats):
        #if the input is a number between 1 and max_seats then return True (is valid)
        if (input.isdigit() and 1 <= int(input) <= max_seats) or input == "":
            return True
        #otherwise return False (don't allow input)
        return False

#function to get a list of available seats for a selected showing and ticket type
def get_available_seats(session, showing_obj, selected_ticket_type):
    #get the selected ticket type's SeatPricing object
    seat_pricing = session.query(SeatPricing).filter(SeatPricing.seat_type == selected_ticket_type).first()

    #get the seat ids for the selected showing that have already been booked (and not cancelled)
    booked_seat_ids = (
        session.query(BookingSeat.seat_id)
        .join(Booking)
        .filter(Booking.showing_id == showing_obj.showing_id, #seat is booked for the selected showing
                Booking.cancelled == False) #booking of the seat is not cancelled
        .subquery()
    )
    
    #query to return available Seat objects
    available_seats = (
        session.query(Seat)
        .filter(
            Seat.screen_id == showing_obj.screen.screen_id, #seat has the same screen as the selected showing
            Seat.pricing_id == seat_pricing.pricing_id, #seat is the same type as the selected ticket
            Seat.available == True,  #seat is available
            ~Seat.seat_id.in_(booked_seat_ids)  #seat is not already booked (or all related bookings are cancelled)
        )
        .all()
    )
    
    #returns list of Seat objects that satisfy the above conditions
    return available_seats

#validate phone number entered
def is_valid_phone(phone):
    #check if the phone number is in the correct format
    phone_pattern = r'^(\+44\s?7\d{3}|\(?0\d{4,5}\)?[\s-]?)\d{3}[\s-]?\d{3}$'
    if not re.match(phone_pattern, phone):
        return "Please enter a valid phone number"
    
#validate card details entered
def is_valid_card(card_number, expiry, cvv):
    #check if the card number is in the correct format
    card_pattern = r'^(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4})$'
    if not re.match(card_pattern, card_number):
        return "Please enter a valid card number"

    #check if the expiry date is in the correct format
    expiry_pattern = r'^(0[1-9]|1[0-2])\/\d{2}$'
    if not re.match(expiry_pattern, expiry):
        return "Please enter a valid expiry date"
    
    #check if the expiry date is in the future
    try:
        #convert expiry date to datetime object
        expiry_date = datetime.strptime(expiry, "%m/%y")

        #get the current date and set the day to the last day of the current month
        current_date = datetime.now().replace(day=1)
        current_date = current_date.replace(month=current_date.month % 12 + 1, day=1) - timedelta(days=1)

        #check if the expiry date is less than or equal to the current date (at the end of the month)
        if expiry_date <= current_date:
            return "The card entered has expired. Please enter a valid expiry date"
    except ValueError:
        return "Please enter a valid expiry date"

    #check if the CVV is in the correct format
    cvv_pattern = r'^\d{3,4}$'
    if not re.match(cvv_pattern, cvv):
        return "Please enter a valid CVV"