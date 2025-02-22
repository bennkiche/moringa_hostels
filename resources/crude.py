from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from models import User, Accommodations, Booking, db, Rooms
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

app = Flask(__name__)

class Users(Resource):
    def get(self, id):
        user = User.query.get(id)
        if not user:
            return {'message': 'User not found'}, 404
        return {'id': user.id, 'name': user.name, 'email': user.email}

    def patch(self, id):
        data = request.get_json()
        
        user = User.query.get(id)
        if not user:
            return {'message': 'User not found'}, 404
        if 'name' in data:
            user.name = data ['name']
        if 'email' in data:
            user.email = data ['email']
        db.session.commit()
        return user.to_dict(), 200

    def delete(self, id):
        user = User.query.get(id)
        if not user:
            return ({'message': 'User not found'}), 404
        db.session.delete(user)
        db.session.commit()
        return {'message': 'User deleted successfully'}

class AccommodationList(Resource):
    @jwt_required()
    def get (self):
        accommodation = Accommodations.query.all()
        if not accommodation:
            return {"error": "Accommodation not found"}, 404
        return [accommo.to_dict() for accommo in accommodation]
    
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return {'error' : 'The user is forbidded from adding new accommodations!'}, 403

        data = request.get_json()
        if not data or not all (key in data for key in ('name', 'image', 'availability', 'price', 'description')):
            return {'error': 'Missing required fields!'}, 422
        
        prices = data['price']
        min = 7000
        max = 30000
        if prices < min or prices > max:
            return {'error' : f'Hostel prices must be between {min} and {max} prices!'},400
        
        new_accommodation = Accommodations(
            name=data ['name'],
            price=prices,
            image=data.get('image'), 
            description=data.get('description'),
            availability=data['availability']
        )
        db.session.add(new_accommodation)
        db.session.commit()
        return new_accommodation.to_dict(), 201

class Accommodation(Resource):
    @jwt_required()
    def get(self, id):
        accommodation = Accommodations.query.get(id)
        return {
            "id": accommodation.id,
            "name": accommodation.name,
            "availability": accommodation.availability
        }
    
    def put(self, id):
        accommodation = Accommodations.query.get(id)
        if not accommodation:
            return {'message': 'Accommodation not found'}, 404
        data = request.get_json()
        accommodation.availability = data.get('availability', accommodation.availability)
        db.session.commit()
        return {
            "id": accommodation.id,
            "name": accommodation.name,
            "availability": accommodation.availability
        },200

    @jwt_required()
    def patch(self, id):
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return {'error' : 'The user is forbidded from editing the accommodations!'}, 403
        
        data = request.get_json()
        accommodation = Accommodations.query.get(id)
        
        if not accommodation:
            return {'message': 'Accommodation not found'}, 404
        if 'name' in data:
            accommodation.name = data ['name']
        if 'price' in data:
            prices = data['price']
            min = 7000
            max = 30000
            if prices < min or prices > max:
                return {'error' : f'Hostel prices must be between {min} and {max} prices!'},400
            accommodation.price = prices
        if 'description' in data:
            accommodation.description = data ['description']
        if 'availability' in data:
            accommodation.availability = data ['availability']
        db.session.commit()
        return accommodation.to_dict(), 200
    @jwt_required()
    def delete(self, id):
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return {'error' : 'The user is forbidded from deleting the accommodations!'}, 403
    
        accommodation = Accommodations.query.get(id)
        if not accommodation:
            return {'message': 'Accommodation not found!'}, 404
        db.session.delete(accommodation)
        db.session.commit()
        return {'message': 'Accommodation deleted successfully!'}
    
# Rooms
class Room(Resource):
    @jwt_required()
    def get (self):
        accommodation = Rooms.query.all()
        if not accommodation:
            return {"error": "Accommodation not found"}, 404
        return [accommo.to_dict() for accommo in accommodation]
    
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return {'error' : 'The user is forbidded from adding new rooms!'}, 403

        data = request.get_json()
        if not data or not all (key in data for key in ('room_no', 'accommodation_id', 'availability')):
            return {'error': 'Missing required fields!'}, 422
        
        new_room = Rooms(
            name=data ['name'],
            room_no = data['room_no'],
            accommodation_id=data.get('accommodation_id'),
            availability=data['availability']
        )
        db.session.add(new_room)
        db.session.commit()
        return new_room.to_dict(), 201

class RoomList(Resource):
    @jwt_required()
    def get(self, id):
        accommodation = Rooms.query.get(id)
        return {
            "id": accommodation.id,
            "room_id": accommodation.room_id,
            "accommodation_id": accommodation.accommodation_id,
            "availability": accommodation.availability
        }
    
    @jwt_required()
    def patch(self, id):
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return {'error' : 'The user is forbidded from editing the accommodations!'}, 403
        
        data = request.get_json()
        accommodation = Rooms.query.get(id)
        
        if not accommodation:
            return {'message': 'Accommodation not found'}, 404
        if 'room_no' in data:
            accommodation.room_no = data ['room_no']
        if 'accommodation_id' in data:
            accommodation.accommodation_id = data ['accommodation_id']
        if 'availability' in data:
            accommodation.availability = data ['availability']
        db.session.commit()
        return accommodation.to_dict(), 200
    
    @jwt_required()
    def delete(self, id):
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return {'error' : 'The user is forbidded from deleting the accommodations!'}, 403
        
        accommodation = Rooms.query.get(id)
        if not accommodation:
            return {'message': 'Accommodation not found!'}, 404
        db.session.delete(accommodation)
        db.session.commit()
        return {'message': 'Accommodation deleted successfully!'}

#Bookings
class BookingsList(Resource):
    @jwt_required()
    def get (self):
        current = get_jwt_identity()
        if current['role'] != 'admin':
            return {'error' : 'the user is not authorized!'}, 403
        
        bookings = Booking.query.all()
        if not bookings:
            return {"error": "Bookings not found!"}, 404
        return [accommo.to_dict() for accommo in bookings]
     
    def post(self):
        data = request.get_json()
        if not data or not all (key in data for key in ('user_id', 'accommodation_id', 'room_id', 'check_in', 'check_out')):
            return {'error': 'Missing required fields!'}, 422
       
        try:
            check_in = datetime.strptime(data['check_in'], "%Y-%m-%dT%H:%M") 
            check_out = datetime.strptime(data['check_out'], "%Y-%m-%dT%H:%M")
        except ValueError:
            return {'error': 'Invalid date format. Use YYYY-MM-DDTHH:MM'}, 400
        
        user_id=data['user_id'],
        accommodation_id=data['accommodation_id'],
        room_id=data['room_id']

        room = Rooms.query.get(room_id)
        if not room or room.accommodation_id != accommodation_id:
            return {"error": "Room does not belong to the accommodation or does not exist!"}, 404

        existing_booking = Booking.query.filter(
            Booking.room_id == room_id,
            Booking.check_out > check_in,
            Booking.check_in < check_out
        ).first()

        if existing_booking:
            return {"error":"Room not available for selected dates!"}
        
        booking = Booking(
            user_id = user_id,
            accommodation_id = accommodation_id,
            room_id = room_id,
            check_in = check_in,
            check_out = check_out
        )

        db.session.add(booking)
        room.availability = "booked!"
        db.session.commit()
        return booking.to_dict(),201
    
    def delete(self, id):
        booking = Booking.query.get(id)
        if not booking:
            return {'message': 'Booking not found!'}, 404
        
        room = booking.room
        if room:
            room.availability = "available!"

        db.session.delete(booking)
        db.session.commit()
        return {'message': 'Booking canceled successfully!'}, 200

class Bookings (Resource):
    def get(self, id):
        booking = Booking.query.get(id)
        if not booking:
            return {'message': 'Booking not found!'}, 404
        return {'id': booking.id, 
                'check_in': str(booking.check_in),
                'check_out': str(booking.check_out)}, 200

