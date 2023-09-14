import boto3
import os
import random

region = "us-east-1"
DYNAMO_DB = "dynamodb"

class HotelDatabase:
    """
    This class handles cancellation, reseravtion and check for room availability.
    The mock hotel management database is set using two dynamodb tables (reservations_table and rooms)

    """
    
    def __init__(self):
        self.dynamodb = boto3.resource(DYNAMO_DB, region_name=region)
        self.rooms_table= self.dynamodb.Table("rooms")
        self.reservation_table= self.dynamodb.Table("reservations_table")

    
    def retrieve_availability(self ,room_type):
        """
        Gets availabilty from room table in dynamodb
        """
        try:
            response = self.rooms_table.get_item(Key={"room_type": room_type})
            availability_info = response["Item"]["availability"]
            return availability_info
        except:
            print("Error while retrieving availability")
            return {'status': False}


    def update_room_count(self, room , update_type):

        """
        Gets current availabilty count of standard , deluxe and suite and 'add' \
        or 'remove' rooms from each item in room dynamodb table.

        Parameters
        room: standard, deluxe, suite
        update_type: add or remove
        """
        try:
            response_rooms = self.rooms_table.get_item(Key={"room_type": room})
            if response_rooms['ResponseMetadata']['HTTPStatusCode'] == 200:
                current_availability = response_rooms["Item"]["availability"]
                if update_type == "remove":
                    availability = int(current_availability) - 1
                
                if update_type == "add":
                    availability = int(current_availability) + 1

            try:
                self.rooms_table.put_item(
                        Item = { 
                            'room_type': room,
                            'availability': str(availability)
                        }
                    )
            except Exception as e:
                print("Error while updating room count")
                return {'status': False, 'cause': e}
            
        except Exception as e:
            print("Error while updating room count")
            return {'status': False, 'cause': e}


    def make_reservation(self ,reservation_id,email, phone, room, check_in):
        """
        Function to make a reservation where reservations dynamodb table is updated with items \
        containing an users reservation id, email , phone , room_type and date of check_in.

        Parameters
        reservation_id : 4 digit random int with # inform ex. #1234
        email: user email
        phone: user phone
        room: standard, deluxe, suite
        check_in: date to check in
        """

        Item = { 
            'reservation_id': str(reservation_id),
            'phone': phone,
            'email': email,
            'room_type': room,
            'check_in': check_in,
        }
        try:
            response = self.reservation_table.put_item(Item=Item)
            if response['ResponseMetadata']['HTTPStatusCode'] ==200:
                self.update_room_count(room, update_type="remove")
                return {'status': "Successful", 'payload': Item , 'cause':"Reservation made successfully"}
       
        except Exception as e:
            return {'status':False, 'cause':e}            
        

    def cancel_reservation(self,reservation_id):

        """
        Function to cancel a reservation. During cancellation item in dyanmodb is removed
        and room counts are deducted based on the specific room type.

        Parameters
        reservation_id : 4 digit random int with # inform ex. #1234
     
        """
        try:
            reservation_info = self.reservation_table.get_item(Key={"reservation_id": reservation_id})
            room = reservation_info['Item']['room_type']
            print(reservation_info['Item']['room_type'])
            try:
                response = self.reservation_table.delete_item(Key={"reservation_id": reservation_id})
                if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                    self.update_room_count(room, update_type="add")
                    return {'status': "Successful", 'cause':"Reservation cancelled successfully"}
            except Exception as e:
                return {'status':False, 'cause':e}  

        except Exception as e:
            return {'status':False, 'cause':e}     

