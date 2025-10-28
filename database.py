from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

DATABASE_URL = "mysql+mysqlconnector://root:naduja@localhost/horizoncinemas"

#create an engine that knows how to connect to MySQL
engine = create_engine(DATABASE_URL, echo=True)

#create all tables defined in models
Base.metadata.create_all(engine)

#create a configured "Session" class
Session = sessionmaker(bind=engine)

#function to get a session
def get_session():
    return Session()
