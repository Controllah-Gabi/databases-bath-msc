from datetime import datetime
from database import Base
from sqlalchemy import Column, Integer, String, Boolean, Date, Time

# Date expects this format "1999-11-07"


class Aircraft(Base):
    __tablename__ = 'Aircrafts'
    id = Column('id', Integer, primary_key=True, index=True)
    type = Column('type', String)


class Flight(Base):
    __tablename__ = 'Flights'
    id = Column('id', Integer, primary_key=True, index=True)
    aircraft = Column('aircraft', String)
    origin = Column('origin', String)
    arrival_terminal = Column('arrival terminal', String)
    origin_terminal = Column('origin terminal', String)
    arrival_gate = Column('arival gate', String)
    departure_gate = Column('departure gate', String)
    route = Column('route', String)
    destination = Column('destination', String)
    arrival_date = Column('arrival date', Date)
    arrival_time = Column('arrival time', Time)
    departure_time = Column('departure time', Time)
    departure_date = Column('departure date', Date)


class Pilot(Base):
    __tablename__ = 'Pilots'
    id = Column('id', Integer, primary_key=True, index=True)
    first_name = Column('first name', String)
    last_name = Column('last name', String)
    date_of_birth = Column('date of birth', Date)
