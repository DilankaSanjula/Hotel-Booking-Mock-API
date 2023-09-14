import boto3
import os
import random

region = "us-east-1"
DYNAMO_DB = "dynamodb"

class HotelDatabase:
    
    def __init__(self):
        self.dynamodb = boto3.resource(DYNAMO_DB, region_name=region)
        self.rooms_table= self.dynamodb.Table("rooms")
        self.reservation_table= self.dynamodb.Table("reservations_table")

    
    def retrieve_availability(self ,room_type):
        response = self.rooms_table.get_item(Key={"room_type": room_type})
        availability_info = response["Item"]["availability"]
        return availability_info


    def update_room_count(self, room , update_type):

        response_rooms = self.rooms_table.get_item(Key={"room_type": room})

        if response_rooms['ResponseMetadata']['HTTPStatusCode'] == 200:
            current_availability = response_rooms["Item"]["availability"]
            if update_type == "remove":
                availability = int(current_availability) - 1
            
            if update_type == "add":
                availability = int(current_availability) + 1

        self.rooms_table.put_item(
                Item = { 
                    'room_type': room,
                    'availability': str(availability)
                }
            )

    def make_reservation(self ,reservation_id,email, phone, room, check_in):

        Item = { 
                'reservation_id': str(reservation_id),
                'phone': phone,
                'email': email,
                'room_type': room,
                'check_in': check_in,
                }
        response = self.reservation_table.put_item(Item=Item)
        if response['ResponseMetadata']['HTTPStatusCode'] ==200:
            self.update_room_count(room, update_type="remove")
            return {'status': "Successful", 'payload': Item , 'cause':"Reservation made successfully"}
        

    def cancel_reservation(self,reservation_id):
        reservation_info = self.reservation_table.get_item(Key={"reservation_id": reservation_id})
        room = reservation_info['Item']['room_type']
        print(reservation_info['Item']['room_type'])

        response = self.reservation_table.delete_item(Key={"reservation_id": reservation_id})
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            self.update_room_count(room, update_type="add")
            return {'status': "Successful", 'cause':"Reservation cancelled successfully"}
