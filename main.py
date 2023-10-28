from fastapi import FastAPI, Depends, HTTPException, Path
from starlette import status
import models
from models import Aircraft, Flight, Pilot
from typing import Annotated
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date, time

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class AircraftRequest(BaseModel):
    type: str


class FlightRequest(BaseModel):
    aircraft: str
    origin: str
    arrival_terminal: str
    origin_terminal: str
    arrival_gate: str
    departure_gate: str
    route: str
    destination: str
    arrival_date: date
    arrival_time: time
    departure_time: time
    departure_date: date


class PilotRequest(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date


@app.get("/aircrafts", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Aircraft).all()


@app.get("/aircrafts/{aircraft_id}", status_code=status.HTTP_200_OK)
async def read_aircraft(db: db_dependency, aircraft_id: int = Path(gt=0)):
    aircraft_model = db.query(Aircraft).filter(
        Aircraft.id == aircraft_id).first()
    if aircraft_model is not None:
        return aircraft_model
    raise HTTPException(status_code=404, detail='Aircraft not found.')


@app.post("/aircraft", status_code=status.HTTP_201_CREATED)
async def create_aircraft(db: db_dependency, aircraft_request: AircraftRequest):
    aircraft_model = Aircraft(**aircraft_request.dict())
    db.add(aircraft_model)
    db.commit()


@app.put("/aircraft/{aircraft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_aircraft(db: db_dependency, aircraft_request: AircraftRequest, aircraft_id: int = Path(gt=0)):
    aircraft_model = db.query(Aircraft).filter(
        Aircraft.id == aircraft_id).first()
    if aircraft_model is None:
        raise HTTPException(status_code=404, detail='Aircraft not found.')

    aircraft_model["type"] = aircraft_request.type

    db.add(aircraft_model)
    db.commit()


@app.delete("/aircraft/{aircraft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pilot(db: db_dependency, aircraft_id: int = Path(gt=0)):
    aircraft_model = db.query(Aircraft).filter(
        Aircraft.id == aircraft_id).first()
    if aircraft_model is None:
        raise HTTPException(status_code=404, detail='Aircraft not found.')
    db.query(Aircraft).filter(Aircraft.id == aircraft_id).delete()

    db.commit()


@app.get("/flights", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Flight).all()


@app.get("/flights/{flight_id}", status_code=status.HTTP_200_OK)
async def read_flight(db: db_dependency, flight_id: int = Path(gt=0)):
    flight_model = db.query(Flight).filter(
        Flight.id == flight_id).first()
    if flight_model is not None:
        return flight_model
    raise HTTPException(status_code=404, detail='Flight not found.')


@app.post("/flights", status_code=status.HTTP_201_CREATED)
async def create_flight(db: db_dependency, flight_request: FlightRequest):
    flight_model = Flight(**flight_request.dict())
    db.add(flight_model)
    db.commit()


@app.put("/flights/{flight_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_pilot(db: db_dependency, flight_request: FlightRequest, flight_id: int = Path(gt=0)):
    flight_model = db.query(Flight).filter(Flight.id == flight_id).first()
    if flight_model is None:
        raise HTTPException(status_code=404, detail='Flight not found.')

    flight_model["aircraft"] = flight_request.aircraft
    flight_model["origin"] = flight_request.origin
    flight_model["arrival terminal"] = flight_request.arrival_terminal
    flight_model["origin terminal"] = flight_request.origin_terminal
    flight_model["arrival gate"] = flight_request.arrival_gate
    flight_model["departure gate"] = flight_request.departure_gate
    flight_model["route"] = flight_request.route
    flight_model["destination"] = flight_request.distination
    flight_model["arrival date"] = flight_request.arrival_date
    flight_model["arrival time"] = flight_request.arrival_time
    flight_model["departure time"] = flight_request.departure_time
    flight_model["departure date"] = flight_request.departure_date

    db.add(flight_model)
    db.commit()


@app.delete("/flights/{flight_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pilot(db: db_dependency, flight_id: int = Path(gt=0)):
    flight_model = db.query(Flight).filter(
        Flight.id == flight_id).first()
    if flight_model is None:
        raise HTTPException(status_code=404, detail='Flight not found.')
    db.query(Flight).filter(Flight.id == flight_id).delete()

    db.commit()


@app.get("/pilots", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Pilot).all()


@app.get("/pilots/{pilot_id}", status_code=status.HTTP_200_OK)
async def read_pilot(db: db_dependency, pilot_id: int = Path(gt=0)):
    pilot_model = db.query(Pilot).filter(
        Pilot.id == pilot_id).first()
    if pilot_model is not None:
        return pilot_model
    raise HTTPException(status_code=404, detail='Pilot not found.')


@app.post("/pilots", status_code=status.HTTP_201_CREATED)
async def create_pilot(db: db_dependency, pilot_request: PilotRequest):
    pilot_model = Pilot(**pilot_request.dict())
    db.add(pilot_model)
    db.commit()


@app.put("/pilots/{pilot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_pilot(db: db_dependency, pilot_request: PilotRequest, pilot_id: int = Path(gt=0)):
    pilot_model = db.query(Pilot).filter(Pilot.id == pilot_id).first()
    if pilot_model is None:
        raise HTTPException(status_code=404, detail='Pilot not found.')

    pilot_model["first name"] = pilot_request.first_name
    pilot_model["last name"] = pilot_request.last_name
    pilot_model["date of birth"] = pilot_request.date_of_birth

    db.add(pilot_model)
    db.commit()


@app.delete("/pilots/{pilot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pilot(db: db_dependency, pilot_id: int = Path(gt=0)):
    pilot_model = db.query(Pilot).filter(
        Pilot.id == pilot_id).first()
    if pilot_model is None:
        raise HTTPException(status_code=404, detail='Pilot not found.')
    db.query(Pilot).filter(Pilot.id == pilot_id).delete()

    db.commit()
