
import uvicorn
from fastapi import FastAPI, Depends, Security, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mock import HotelDatabase


app = FastAPI()
db_functions = HotelDatabase()

class Reservation(BaseModel):
    reservation_id: str
    user_email: str
    user_phone: str
    room_type: str
    check_in_date: str

class RoomType(BaseModel):
    room_type: str

class CancelReservation(BaseModel):
    reservation_id: str

@app.get("/")
async def root() -> int:
    return 200


@app.post("/availability")
async def check_availability(room_info: RoomType):
    room_type = room_info.room_type
    availability_response = db_functions.retrieve_availability(room_type)
    return availability_response

@app.post("/reserve")
async def make_reservation(reservation_params: Reservation):
    email = reservation_params.user_email
    phone = reservation_params.user_phone
    room = reservation_params.room_type
    check_in = reservation_params.check_in_date
    reservation_id = reservation_params.reservation_id

    reservation_response = db_functions.make_reservation(reservation_id,email, phone, room, check_in)
    return reservation_response


@app.post("/cancel_reservation")
async def cancel_reservation(reservation_info: CancelReservation):
    cancelation_response = db_functions.cancel_reservation(reservation_info.reservation_id)
    return cancelation_response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7005, proxy_headers=True)

