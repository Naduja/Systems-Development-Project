from sqlalchemy import Column, Integer, VARCHAR, DECIMAL, Boolean, ForeignKey, DateTime, NVARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import YEAR, TINYINT

Base = declarative_base()

#main tables
class City(Base):
    __tablename__ = 'city'
    city_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(20), nullable=False)
    morning_price = Column(DECIMAL(4, 2), nullable=False)
    afternoon_price = Column(DECIMAL(4, 2), nullable=False)
    evening_price = Column(DECIMAL(4, 2), nullable=False)
    #1-many relationship with cinema
    cinemas = relationship('Cinema', back_populates='city', cascade='all, delete, delete-orphan')

class Policy(Base):
    __tablename__ = 'policy'
    policy_id = Column(Integer, primary_key=True, autoincrement=True)
    refund_percentage = Column(DECIMAL(6, 3), nullable=False)
    min_days_for_refund = Column(TINYINT(unsigned=True), nullable=False)
    max_days_for_booking = Column(TINYINT(unsigned=True), nullable=False)
    min_screens_per_cinema = Column(TINYINT(unsigned=True), nullable=False)
    max_screens_per_cinema = Column(TINYINT(unsigned=True), nullable=False)
    min_shows_per_day = Column(TINYINT(unsigned=True), nullable=False)
    max_shows_per_day = Column(TINYINT(unsigned=True), nullable=False)
    min_seats_per_screen = Column(TINYINT(unsigned=True), nullable=False)
    max_seats_per_screen = Column(TINYINT(unsigned=True), nullable=False)
    min_VIP = Column(TINYINT(unsigned=True), nullable=False)
    max_VIP = Column(TINYINT(unsigned=True), nullable=False)
    lower_hall_percentage = Column(DECIMAL(5, 2), nullable=False) 
    
class Cinema(Base):
    __tablename__ = 'cinema'
    cinema_id = Column(Integer, primary_key=True, autoincrement=True)
    neighbourhood = Column(VARCHAR(60), nullable=False)
    available = Column(Boolean, nullable=False, default=True)
    #foreign keys
    city_id = Column(Integer, ForeignKey('city.city_id', ondelete='CASCADE'), nullable=False)
    #many-1 relationship with city
    city = relationship('City', back_populates='cinemas')
    #1-many relationships with screen and staff
    screens = relationship('Screen', back_populates='cinema', cascade='all, delete, delete-orphan')
    staff = relationship('Staff', back_populates='cinema') 

class Screen(Base):
    __tablename__ = 'screen'
    screen_id = Column(Integer, primary_key=True, autoincrement=True)
    num_lower_gallery = Column(TINYINT(unsigned=True), nullable=False)
    num_upper_gallery = Column(TINYINT(unsigned=True), nullable=False)  
    num_VIP = Column(TINYINT(unsigned=True), nullable=False)
    available = Column(Boolean, nullable=False, default=True)
    #foreign key
    cinema_id = Column(Integer, ForeignKey('cinema.cinema_id', ondelete='CASCADE'), nullable=False)
    #many-1 relationship with cinema
    cinema = relationship('Cinema', back_populates='screens')
    #1-many relationships with seat and showing
    seats = relationship('Seat', back_populates='screen', cascade='all, delete, delete-orphan')
    showings = relationship('Showing', back_populates='screen', cascade='all, delete, delete-orphan')

class Film(Base):
    __tablename__ = 'film'
    film_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(200), nullable=False)
    description = Column(VARCHAR(2000), nullable=False)
    age_rating = Column(VARCHAR(10), nullable=False)
    imdb = Column(DECIMAL(3, 1), nullable=False)
    duration = Column(Integer, nullable=False)
    release_year = Column(YEAR, nullable=False)
    #1-many relationships with showing, actorfilm and genrefilm
    showings = relationship('Showing', back_populates='film', cascade='all, delete, delete-orphan')
    actorfilms = relationship('ActorFilm', back_populates='film', cascade='all, delete, delete-orphan')
    genrefilms = relationship('GenreFilm', back_populates='film', cascade='all, delete, delete-orphan')

class Showing(Base):
    __tablename__ = 'showing'
    showing_id = Column(Integer, primary_key=True, autoincrement=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    #foreign keys
    screen_id = Column(Integer, ForeignKey('screen.screen_id', ondelete='CASCADE'), nullable=False)
    film_id = Column(Integer, ForeignKey('film.film_id', ondelete='CASCADE'), nullable=False)
    #many-1 relationships with screen and film
    screen = relationship('Screen', back_populates='showings')
    film = relationship('Film', back_populates='showings')
    #1-many relationship with booking
    bookings = relationship('Booking', back_populates='showing')

class Actor(Base):
    __tablename__ = 'actor'
    actor_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(100), nullable=False)
    #1-many relationship with actorfilm
    actorfilms = relationship('ActorFilm', back_populates='actor', cascade='all, delete, delete-orphan')

class ActorFilm(Base):
    __tablename__ = 'actorfilm'
    actor_id = Column(Integer, ForeignKey('actor.actor_id', ondelete='CASCADE'), primary_key=True)
    film_id = Column(Integer, ForeignKey('film.film_id', ondelete='CASCADE'), primary_key=True)
    #many-1 relationships with actor and film
    actor = relationship('Actor', back_populates='actorfilms')
    film = relationship('Film', back_populates='actorfilms')

class Genre(Base):
    __tablename__ = 'genre'
    genre_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(50), nullable=False)
    #1-many relationship with genrefilm
    genrefilms = relationship('GenreFilm', back_populates='genre', cascade='all, delete, delete-orphan')

class GenreFilm(Base):
    __tablename__ = 'genrefilm'
    genre_id = Column(Integer, ForeignKey('genre.genre_id', ondelete='CASCADE'), primary_key=True)
    film_id = Column(Integer, ForeignKey('film.film_id', ondelete='CASCADE'), primary_key=True)
    #many-1 relationships with genre and film
    genre = relationship('Genre', back_populates='genrefilms')
    film = relationship('Film', back_populates='genrefilms')

class SeatPricing(Base):
    __tablename__ = 'seatpricing'
    pricing_id = Column(Integer, primary_key=True, autoincrement=True)
    seat_type = Column(VARCHAR(40), nullable=False)
    multiplier = Column(DECIMAL(5, 3), nullable=False)
    #1-many relationship with seat
    seats = relationship('Seat', back_populates='seatpricing')

class Seat(Base):
    __tablename__ = 'seat'
    seat_id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(TINYINT(unsigned=True), nullable=False)
    available = Column(Boolean, nullable=False, default=True)
    #foreign keys
    screen_id = Column(Integer, ForeignKey('screen.screen_id', ondelete='CASCADE'), nullable=False)
    pricing_id = Column(Integer, ForeignKey('seatpricing.pricing_id', ondelete='RESTRICT'), nullable=False)
    #many-1 relationships with screen and seatpricing
    screen = relationship('Screen', back_populates='seats')
    seatpricing = relationship('SeatPricing', back_populates='seats')
    #1-many relationship with bookingseat
    bookingseats = relationship('BookingSeat', back_populates='seat', cascade='all, delete, delete-orphan')

class Role(Base):
    __tablename__ = 'role'
    role_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(VARCHAR(50), unique=True, nullable=False)
    #1-many relationship with staff
    staff = relationship('Staff', back_populates='role')

class Staff(Base):
    __tablename__ = 'staff'
    staff_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(100), nullable=False)
    email = Column(NVARCHAR(320), unique=True, nullable=False)
    password = Column(VARCHAR(255), nullable=False)
    #foreign keys
    cinema_id = Column(Integer, ForeignKey('cinema.cinema_id', ondelete='RESTRICT'), nullable=False)
    role_id = Column(Integer, ForeignKey('role.role_id', ondelete='RESTRICT'), nullable=False)
    #many-1 relationships with cinema and role
    cinema = relationship('Cinema', back_populates='staff')
    role = relationship('Role', back_populates='staff')
    #1-many relationship with booking
    bookings = relationship('Booking', back_populates='staff')

class Booking(Base):
    __tablename__ = 'booking'
    booking_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_name = Column(VARCHAR(100), nullable=False)
    customer_email = Column(NVARCHAR(320), nullable=False)
    customer_phone = Column(VARCHAR(20), nullable=False)
    booking_date = Column(DateTime, nullable=False)
    booking_cost = Column(DECIMAL(6, 2), nullable=False)
    cancelled = Column(Boolean, nullable=False)
    refund_amount = Column(DECIMAL(6, 2), nullable=False, default=0)
    #foreign keys
    showing_id = Column(Integer, ForeignKey('showing.showing_id', ondelete='SET NULL'))
    staff_id = Column(Integer, ForeignKey('staff.staff_id', ondelete='SET NULL'))
    #many-1 relationships with showing and staff
    showing = relationship('Showing', back_populates='bookings')
    staff = relationship('Staff', back_populates='bookings')
    #1-many relationship with bookingseat
    bookingseats = relationship('BookingSeat', back_populates='booking', cascade='all, delete, delete-orphan')

class BookingSeat(Base):
    __tablename__ = 'bookingseat'
    booking_id = Column(Integer, ForeignKey('booking.booking_id', ondelete='CASCADE'), primary_key=True)
    seat_id = Column(Integer, ForeignKey('seat.seat_id', ondelete='CASCADE'), primary_key=True)
    #many-1 relationships with booking and seat
    seat = relationship('Seat', back_populates='bookingseats')
    booking = relationship('Booking', back_populates='bookingseats')