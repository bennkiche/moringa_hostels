from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from models import User, Accommodations, Booking, db
from datetime import datetime

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
    def get (self):
        accommodation = Accommodations.query.all()
        if not accommodation:
            return {"error": "Accommodation not found"}, 404
        return [accommo.to_dict() for accommo in accommodation]

    def post(self):
        data = request.get_json()
        if not data or not all (key in data for key in ('name', 'image', 'availability', 'price', 'description', 'user_id')):
            return {'error': 'Missing required fields!'}, 422
        new_accommodation = Accommodations(
            name=data ['name'],
            user_id=data['user_id'], 
            price=data['price'],
            image=data.get('image'), 
            description=data.get('description'),
            availability=data['availability']
        )
        db.session.add(new_accommodation)
        db.session.commit()
        return new_accommodation.to_dict(), 201

class Accommodation(Resource):
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


    def patch(self, id):
        data = request.get_json()
        accommodation = Accommodations.query.get(id)
        
        if not accommodation:
            return {'message': 'Accommodation not found'}, 404
        if 'name' in data:
            accommodation.name = data ['name']
        if 'user_id' in data:
            accommodation.user_id = data ['user_id']
        if 'price' in data:
            accommodation.price = data ['price']
        if 'description' in data:
            accommodation.description = data ['description']
        if 'availability' in data:
            accommodation.availability = data ['availability']
        db.session.commit()
        return accommodation.to_dict(), 200
  
    def delete(self, id):
        accommodation = Accommodations.query.get(id)
        if not accommodation:
            return {'message': 'Accommodation not found!'}, 404
        db.session.delete(accommodation)
        db.session.commit()
        return {'message': 'Accommodation deleted successfully!'}

#Bookings
class BookingsList(Resource):
    def get (self):
        bookings = Booking.query.all()
        if not bookings:
            return {"error": "Bookings not found!"}, 404
        return [accommo.to_dict() for accommo in bookings]
     
    def post(self):
        data = request.get_json()
        if not data or not all (key in data for key in ('user_id', 'accommodation_id', 'check_in', 'check_out')):
            return {'error': 'Missing required fields!'}, 422
       

        try:
            check_in = datetime.strptime(data['check_in'], "%Y-%m-%dT%H:%M") 
            check_out = datetime.strptime(data['check_out'], "%Y-%m-%dT%H:%M")
        except ValueError:
            return {'error': 'Invalid date format. Use YYYY-MM-DDTHH:MM'}, 400
        
        user_id=data['user_id'],
        accommodation_id=data['accommodation_id'],
        existing_booking = Booking.query.filter(
            Booking.accommodation_id == accommodation_id,
            Booking.check_out > check_in,
            Booking.check_in < check_out
        ).first()
        if existing_booking:
            return {"error":"Accommodation not available for selected dates!"}
        booking = Booking(
            user_id = user_id,
            accommodation_id = accommodation_id,
            check_in = check_in,
            check_out = check_out
        )
        db.session.add(booking)
        accommodation = Accommodations.query.get(accommodation_id)
        if accommodation:
            accommodation.availability = "booked!"
        db.session.commit()
        return booking.to_dict(),201
    
    def delete(self, id):
        booking = Booking.query.get(id)
        if not booking:
            return {'message': 'Booking not found!'}, 404

        accommodation = Accommodations.query.get(booking.accommodation_id)
        if accommodation:
            accommodation.availability = "available!"

        db.session.delete(booking)
        db.session.commit()
        return {'message': 'Booking canceled successfully'}, 200

class Bookings (Resource):
    def get(self, id):
        booking = Booking.query.get(id)
        if not booking:
            return {'message': 'Booking not found!'}, 404
        return {'id': booking.id, 
                'check_in': str(booking.check_in),
                'check_out': str(booking.check_out)}, 200

