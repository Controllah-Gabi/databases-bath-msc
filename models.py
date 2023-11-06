from datetime import datetime
from database import Base
from sqlalchemy import Column, Integer, String, Boolean, Date, Time, ForeignKey, Table
from sqlalchemy.orm import relationship

# Many-to-Many relationship between Flights and Pilots
flight_pilot_association = Table('flight_pilot_association', Base.metadata,
                                 Column('flight_id', Integer,
                                        ForeignKey('Flights.id')),
                                 Column('pilot_id', Integer,
                                        ForeignKey('Pilots.id'))
                                 )


class Aircraft(Base):
    __tablename__ = 'Aircrafts'

    id = Column('id', Integer, primary_key=True, index=True)
    type = Column('type', String)
    # One-to-Many relationship with Flight
    flights = relationship("Flight", back_populates="aircraft")


class Flight(Base):
    __tablename__ = 'Flights'

    id = Column('id', Integer, primary_key=True, index=True)
    aircraft_id = Column(Integer, ForeignKey('Aircrafts.id'))
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

    # Many-to-Many relationship with Pilot
    pilots = relationship(
        "Pilot", secondary=flight_pilot_association, back_populates="flights")

    # Back reference to Aircraft
    aircraft = relationship("Aircraft", back_populates="flights")


class Pilot(Base):
    __tablename__ = 'Pilots'

    id = Column('id', Integer, primary_key=True, index=True)
    first_name = Column('first name', String)
    last_name = Column('last name', String)
    date_of_birth = Column('date of birth', Date)
    # Many-to-Many relationship with Flight
    flights = relationship(
        "Flight", secondary=flight_pilot_association, back_populates="pilots")
