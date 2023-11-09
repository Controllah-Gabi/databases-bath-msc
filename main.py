from fastapi import FastAPI, Depends, HTTPException, Path
from starlette import status
import models
from models import Aircraft, Flight, Pilot
from typing import Annotated
from database import engine, SessionLocal
from sqlalchemy.orm import Session, sessionmaker
from pydantic import BaseModel
from datetime import date, time
from sqlalchemy import func
import uvicorn

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class FlightPilotLinkRequest(BaseModel):
    pilot_id: int
    flight_id: int


class AircraftRequest(BaseModel):
    type: str


class FlightRequest(BaseModel):
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
    aircraft_id: int


class PilotRequest(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date


@app.get("/aircrafts", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Aircraft).all()


@app.get("/aircrafts/{aircraft_id}", status_code=status.HTTP_200_OK)
async def read_aircraft(db: db_dependency, aircraft_id: int = Path(gt=0)):
    # Query the database for the specified aircraft by ID.
    aircraft_model = db.query(Aircraft).filter(
        Aircraft.id == aircraft_id).first()

    # If the aircraft is found, return its data.
    if aircraft_model:
        return aircraft_model
    # If the aircraft is not found, raise an HTTP 404 error.
    else:
        raise HTTPException(status_code=404, detail='Aircraft not found.')


@app.get("/aircrafts/{aircraft_id}/flights", status_code=status.HTTP_200_OK)
async def read_aircraft_flights(db: db_dependency, aircraft_id: int = Path(gt=0)):
    # Attempt to retrieve the aircraft by its ID from the database.
    aircraft_model = db.query(Aircraft).filter(
        Aircraft.id == aircraft_id).first()

    # If the aircraft exists, return the list of associated flights.
    if aircraft_model:
        return aircraft_model.flights
    # If the aircraft does not exist, raise a 404 error.
    else:
        raise HTTPException(status_code=404, detail='Aircraft not found.')


@app.post("/aircraft", status_code=status.HTTP_201_CREATED)
async def create_aircraft(db: db_dependency, aircraft_request: AircraftRequest):
    # Create a new Aircraft instance from the request body.
    aircraft_model = Aircraft(**aircraft_request.dict())

    # Add the new aircraft to the database session and commit the transaction.
    db.add(aircraft_model)
    db.commit()

    # Return the created aircraft model to the client.
    return aircraft_model


@app.put("/aircraft/{aircraft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_aircraft(
    db: db_dependency,
    aircraft_request: AircraftRequest,
    aircraft_id: int = Path(gt=0)
):
    # Attempt to retrieve the aircraft by the provided ID.
    aircraft_model = db.query(Aircraft).filter(
        Aircraft.id == aircraft_id).first()

    # If the aircraft doesn't exist, return a 404 error.
    if aircraft_model is None:
        raise HTTPException(status_code=404, detail='Aircraft not found.')

    # Update the aircraft's type with the new value.
    aircraft_model.type = aircraft_request.type

    # Persist the changes to the database.
    db.add(aircraft_model)
    db.commit()


@app.delete("/aircraft/{aircraft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_aircraft(db: db_dependency, aircraft_id: int = Path(gt=0)):
    # Attempt to retrieve the aircraft by ID.
    aircraft_model = db.query(Aircraft).filter(
        Aircraft.id == aircraft_id).first()

    # If no aircraft is found, return a 404 error.
    if aircraft_model is None:
        raise HTTPException(status_code=404, detail='Aircraft not found.')

    # If the aircraft is found, delete it from the database.
    db.query(Aircraft).filter(Aircraft.id == aircraft_id).delete()
    # Commit the changes to the database.
    db.commit()


@app.get("/flights", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Flight).all()


@app.get("/flights/statistics", status_code=status.HTTP_200_OK)
async def flight_statistics(db: db_dependency):
    """
    Retrieve statistics about flights including total number of flights, most common destination, 
    and most commonly used aircraft type.

    This endpoint does not require any parameters and provides a summary of the flight data 
    available in the database.

    Parameters:
    - db: db_dependency - The database session dependency injected into the function.

    Returns:
    A JSON object with three fields:
    - 'total_flights': An integer representing the total number of flights.
    - 'most_common_destination': An object containing the most common destination and its count.
    - 'most_common_aircraft': An object containing the most commonly used aircraft type and its count.

    Example response:
    ```
    {
        "total_flights": 250,
        "most_common_destination": {
            "destination": "LAX",
            "count": 75
        },
        "most_common_aircraft": {
            "aircraft_type": "Boeing 737",
            "count": 120
        }
    }
    ```

    The 'most_common_destination' and 'most_common_aircraft' are calculated by counting the occurrences
    of each destination and aircraft type respectively, and then ordering in descending order to find 
    the most frequent.
    """
    # Calculate the total number of flights.
    total_flights = db.query(func.count(Flight.id)).scalar()

    # Determine the most common destination for the flights.
    most_common_destination = db.query(
        Flight.destination,
        func.count(Flight.destination).label('destination_count')
    ).group_by(Flight.destination).order_by(func.count(Flight.destination).desc()).first()

    # Find out which aircraft type is most commonly used on the flights.
    most_common_aircraft = db.query(
        Aircraft.type,
        func.count(Flight.aircraft_id).label('aircraft_count')
    ).join(Flight, Aircraft.id == Flight.aircraft_id)\
        .group_by(Aircraft.type)\
        .order_by(func.count(Flight.aircraft_id).desc()).first()

    # Format and return the statistics as a JSON object.
    return {
        'total_flights': total_flights,
        'most_common_destination': {
            'destination': most_common_destination.destination,
            'count': most_common_destination.destination_count
        },
        'most_common_aircraft': {
            'aircraft_type': most_common_aircraft.type,
            'count': most_common_aircraft.aircraft_count
        }
    }


@app.get("/flights/{flight_id}", status_code=status.HTTP_200_OK)
async def read_flight(db: db_dependency, flight_id: int = Path(gt=0)):
  # Attempt to retrieve the flight from the database using the given flight_id.
    flight_model = db.query(Flight).filter(Flight.id == flight_id).first()

    # If the flight exists, return its data.
    if flight_model is not None:
        return flight_model

    # If the flight does not exist, raise a 404 error to indicate it was not found.
    raise HTTPException(status_code=404, detail='Flight not found.')


@app.get("/flights/{flight_id}/pilots", status_code=status.HTTP_200_OK)
async def read_flight_pilots(db: db_dependency, flight_id: int = Path(gt=0)):
    # Fetch the flight from the database using the provided flight_id.
    flight_model = db.query(Flight).filter(Flight.id == flight_id).first()

    # If the flight is found, return the list of pilots assigned to this flight.
    if flight_model is not None:
        return flight_model.pilots

    # If the flight is not found, raise a 404 error.
    raise HTTPException(status_code=404, detail='Flight not found.')


@app.post("/flights", status_code=status.HTTP_201_CREATED)
async def create_flight(db: db_dependency, flight_request: FlightRequest):
    # Convert the request payload to a Flight model instance.
    flight_model = Flight(**flight_request.dict())

    # Add the new Flight record to the database.
    db.add(flight_model)

    # Commit the transaction to save the changes.
    db.commit()

    # Return the new Flight record.
    return flight_model


@app.put("/flights/{flight_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_flight(db: db_dependency, flight_request: FlightRequest, flight_id: int = Path(gt=0)):
    # Updates a flight's information in the database.

    # Retrieve the existing flight from the database
    flight_model = db.query(Flight).filter(Flight.id == flight_id).first()

    # If the flight does not exist, return a "not found" response
    if flight_model is None:
        raise HTTPException(status_code=404, detail='Flight not found.')

    # Update the flight's attributes with the new values from flight_request
    flight_model.origin = flight_request.origin
    flight_model.aircraft_id = flight_request.aircraft_id
    flight_model.arrival_terminal = flight_request.arrival_terminal
    flight_model.origin_terminal = flight_request.origin_terminal
    flight_model.arrival_gate = flight_request.arrival_gate
    flight_model.departure_gate = flight_request.departure_gate
    flight_model.route = flight_request.route
    flight_model.destination = flight_request.destination
    flight_model.arrival_date = flight_request.arrival_date
    flight_model.arrival_time = flight_request.arrival_time
    flight_model.departure_time = flight_request.departure_time
    flight_model.departure_date = flight_request.departure_date

    # Update the flight record in the database
    db.add(flight_model)

    # Commit the changes to the database to save the updated flight information
    db.commit()


@app.delete("/flights/{flight_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flight(db: db_dependency, flight_id: int = Path(gt=0)):

    # Fetch the flight by ID to check if it exists
    flight_model = db.query(Flight).filter(Flight.id == flight_id).first()

    # If the flight doesn't exist, return a "not found" response
    if flight_model is None:
        raise HTTPException(status_code=404, detail='Flight not found.')

    # If the flight exists, delete it from the database
    db.query(Flight).filter(Flight.id == flight_id).delete()

    # Commit the changes to the database to finalize the deletion
    db.commit()


@app.get("/pilots", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    # Returns:
    # - A list of Pilot objects in JSON format.
    # - Each Pilot object contains all attributes of a pilot as defined in the model.

    # Execute the query to get all pilots and return them.
    return db.query(Pilot).all()


@app.post("/link-pilot-flight/", status_code=status.HTTP_201_CREATED)
async def link_pilot_to_flight(request: FlightPilotLinkRequest, db: db_dependency):
    # Check if the flight exists
    flight = db.query(Flight).filter(Flight.id == request.flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail='Flight not found.')

    # Check if the pilot exists
    pilot = db.query(Pilot).filter(Pilot.id == request.pilot_id).first()
    if not pilot:
        raise HTTPException(status_code=404, detail='Pilot not found.')

    # Link the pilot to the flight
    pilot.flights.append(flight)
    db.commit()
    return {"message": "Pilot linked to flight successfully"}


@app.get("/pilots/{pilot_id}", status_code=status.HTTP_200_OK)
async def read_pilot(db: db_dependency, pilot_id: int = Path(gt=0)):
    # Query the database to retrieve the first pilot whose ID matches the provided pilot_id.
    # The method .first() will return the pilot object if found, or None if no match exists.
    pilot_model = db.query(Pilot).filter(Pilot.id == pilot_id).first()

    # Check if the pilot_model is not None, which means a record was found.
    if pilot_model is not None:
        # If the pilot is found, return the pilot model object.
        # This object includes details like ID, first name, last name, etc.
        return pilot_model

    # If the pilot_model is None, meaning no pilot was found with the provided ID,
    # raise an HTTPException with status code 404 for Not Found.
    # The provided detail 'Pilot not found.' will be returned as the error message.
    raise HTTPException(status_code=404, detail='Pilot not found.')


@app.get("/pilots/{pilot_id}/flights", status_code=status.HTTP_200_OK)
async def read_pilot_flights(db: db_dependency, pilot_id: int = Path(gt=0)):
    # Query the database to find the first pilot whose ID matches the provided pilot_id.
    # The `.first()` method returns the first match or None if no match is found.
    pilot = db.query(Pilot).filter(Pilot.id == pilot_id).first()

    # Check if a pilot was found with the given ID.
    if pilot:
        # If the pilot exists, return the list of associated flights.
        # The `pilot.flights` accesses the related flights through the many-to-many relationship.
        return pilot.flights
    else:
        # If no pilot is found, raise an HTTPException with a 404 status code indicating "Not Found".
        # The error message 'Pilot not found' will be displayed to the user.
        raise HTTPException(status_code=404, detail='Pilot not found.')


@app.post("/pilots", status_code=status.HTTP_201_CREATED)
async def create_pilot(db: db_dependency, pilot_request: PilotRequest):
    # Create a new pilot instance using the data provided in the pilot_request
    # The **pilot_request.dict() unpacks the pilot_request into the Pilot model
    pilot_model = Pilot(**pilot_request.dict())

    # Add the new pilot instance to the database session
    # This stages the new pilot for insertion into the database
    db.add(pilot_model)

    # Commit the session to insert the new pilot record into the database
    # After this call, the pilot data will be permanently in the database
    db.commit()

    # The function implicitly returns None, which is fine here since
    # we're not expecting to send any data back on successful creation
    # The status code 201 Created is sent back to the client to indicate success


@app.put("/pilots/{pilot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_pilot(db: db_dependency, pilot_request: PilotRequest, pilot_id: int = Path(gt=0)):
    # Retrieve the pilot with the given pilot_id from the database
    pilot_model = db.query(Pilot).filter(Pilot.id == pilot_id).first()

    # If no pilot is found with the given ID, raise a 404 error
    if pilot_model is None:
        raise HTTPException(status_code=404, detail='Pilot not found.')

    # Update the pilot's information with data from the request
    pilot_model.first_name = pilot_request.first_name
    pilot_model.last_name = pilot_request.last_name
    pilot_model.date_of_birth = pilot_request.date_of_birth
    # Be cautious with updating flight_id directly, it should be handled with care in a many-to-many relationship
    pilot_model.flight_id = pilot_request.flight_id

    # Stage the updated pilot model for committing to the database
    db.add(pilot_model)
    # Commit the transaction to save the updated pilot information in the database
    db.commit()


@app.delete("/pilots/{pilot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pilot(db: db_dependency, pilot_id: int = Path(gt=0)):
    # Retrieve the pilot with the given pilot_id from the database
    pilot_model = db.query(Pilot).filter(
        Pilot.id == pilot_id).first()

    # If a pilot with the given ID does not exist, raise a 404 error
    if pilot_model is None:
        raise HTTPException(status_code=404, detail='Pilot not found.')

    # Delete the pilot record from the database
    db.query(Pilot).filter(Pilot.id == pilot_id).delete()

    # Commit the transaction to make sure the deletion is saved in the database
    db.commit()

uvicorn.run(app, host="0.0.0.0", port="8080")
