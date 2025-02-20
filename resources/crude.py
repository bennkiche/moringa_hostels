#users(students and hosts)
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from models import User, Accommodations, Booking, db

app = Flask(__name__)

class Users(Resource):
    def get_user(self):
        user = User.query.get(id)
        if not user:
            return {'message': 'User not found'}, 404
        return {'id': user.id, 'name': user.name, 'email': user.email}

    def patch(self):
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

    def delete(self):
        user = User.query.get(id)
        if not user:
            return ({'message': 'User not found'}), 404
        db.session.delete(user)
        db.session.commit()
        return {'message': 'User deleted successfully'}

#Accommodation
class AccommodationList(Resource):
    def post(self):
        data = request.get_json()
        if not data or not all (key in data for key in ('name', 'image', 'availability', 'price', 'description', 'id')):
            return {'error': 'Missing required fields!'}, 422
        new_accommodation = Accommodations(
            name=data ['name'],
            user_id=data['id'], price=data['price'],
            image=data.get('image'), description=data.get('description'),
            availability=data['availability']
        )
        db.session.add(new_accommodation)
        db.session.commit()
        return new_accommodation.to_dict(), 201

class Accommodation(Resource):
    def get(self):
        accommodations = Accommodations.query.get(id)
        if not accommodations:
            return {'message': 'Accommodation not found'}, 404
        return [{'id': accommodation.id,'name': accommodation.name, 'price': str(accommodation.price), 'description': accommodation.description} for accommodation in accommodations]

    def patch(self):
        data = request.get_json
        accommodation = Accommodations.query.get(id)
        
        if not accommodation:
            return {'message': 'Accommodation not found'}, 404
        if 'name' in data:
            accommodation.name = data ['name']
        if 'price' in data:
            accommodation.price = data ['price']
        if 'description' in data:
            accommodation.description = data ['description']
        if 'availability' in data:
            accommodation.availability = data ['availability']
        db.session.commit()
        return accommodation.to_dict(), 200
  
    def delete(self):
        accommodation = Accommodations.query.get(id)
        if not accommodation:
            return {'message': 'Accommodation not found'}, 404
        db.session.delete(accommodation)
        db.session.commit()
        return {'message': 'Accommodation deleted successfully'}

#Bookings
class BookingsList(Resource):
    def post(self):
        data = request.get_json()
        if not data or not all (key in data for key in ('user_id', 'accommodation_id', 'check_in', 'check_out')):
            return {'error': 'Missing required fields!'}, 422
        new_booking = Booking(user_id=data['user_id'], accommodation_id=data['accommodation_id'],
                            check_in=data['check_in'], check_out=data['check_out'])
        db.session.add(new_booking)
        db.session.commit()
        return {'message': 'Booking created successfully'}, 201

class Bookings (Resource):
    def get(self):
        booking = Booking.query.get(id)
        if not booking:
            return {'message': 'Booking not found'}, 404
        return {'id': booking.id, 'check_in': str(booking.check_in), 'check_out': str(booking.check_out)}

    def delete(self):
        booking = Booking.query.get(id)
        if not booking:
            return {'message': 'Booking not found'}, 404
        db.session.delete(booking)
        db.session.commit()
        return {'message': 'Booking canceled successfully'}

