from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from models import User, Accommodations, Booking, db, Rooms, Reviews
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash
from flask_bcrypt import Bcrypt
from flask_jwt_extended import jwt_required, get_jwt_identity

app = Flask(__name__)
bcrypt = Bcrypt(app)

class Users(Resource):
    def get(self, id):
        user = User.query.get(id)
        if not user:
            return {'message': 'User not found'}, 404
        return {'id': user.id, 'name': user.name, 'email': user.email}

    

class Users(Resource):
    @jwt_required()
    def patch(self, id):
        user = User.query.get(id)

        if not user:
            return {'error': 'User not found'}, 404

        print(f"User found: {user.id}, Stored password: {user.password}")  # Debugging

        data = request.get_json()
        print(f"Received data: {data}")  # Debugging

        current_password = data.get('current_password')

        # Check if current password is provided
        if not current_password:
            return {'error': 'Current password is required'}, 400

        try:
            if not check_password_hash(user.password, current_password):
                return {'error': 'Incorrect current password'}, 401
        except ValueError as e:
            return {'error': f'Invalid password hash: {str(e)}'}, 400

        # Allow updates for name, email, and password
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            user.email = data['email']
        if 'new_password' in data:
            user.password = bcrypt.generate_password_hash(data['new_password']).decode('utf-8')

        db.session.commit()
        return {'message': 'Profile updated successfully'}, 200


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
    
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return {'error' : 'The user is forbidden from adding new accommodations!'}, 403

        data = request.get_json()
        if not data or not all (key in data for key in ('name', 'image', 'description')):
            return {'error': 'Missing required fields!'}, 422
        
        new_accommodation = Accommodations(
            name=data ['name'],
            image=data.get('image'), 
            description=data.get('description')
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
            "description": accommodation.description
        }
    
    def put(self, id):
        accommodation = Accommodations.query.get(id)
        if not accommodation:
            return {'message': 'Accommodation not found'}, 404
        data = request.get_json()
        availability = data.get('availability')
        if availability is not None:
            accommodation.availability = availability
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
            return {'error' : 'The user is forbidden from editing the accommodations!'}, 403
        
        data = request.get_json()
        accommodation = Accommodations.query.get(id)
        
        if not accommodation:
            return {'message': 'Accommodation not found'}, 404
        if 'name' in data:
            accommodation.name = data ['name']
        if 'description' in data:
            accommodation.description = data ['description']
        if 'image' in data:
            accommodation.image = data ['image']
        db.session.commit()
        return accommodation.to_dict(), 200
    @jwt_required()
    def delete(self, id):
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return {'error' : 'The user is forbidden from deleting the accommodations!'}, 403
    
        accommodation = Accommodations.query.get(id)
        if not accommodation:
            return {'message': 'Accommodation not found!'}, 404
        db.session.delete(accommodation)
        db.session.commit()
        return {'message': 'Accommodation and its associated rooms have been deleted successfully!'}, 200
    
# Rooms
class Room(Resource):
    def get (self):
        accommodation = Rooms.query.all()
        if not accommodation:
            return {"error": "rooms not found"}, 404
        return [accommo.to_dict() for accommo in accommodation]
    
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return {'error' : 'The user is forbidden from adding new rooms!'}, 403

        data = request.get_json()
        if not data or not all (key in data for key in ('room_no','room_type','price', 'accommodation_id', 'availability', 'image', 'description')):
            return {'error': 'Missing required fields!'}, 422
        
        room_no = data['room_no']
        min = 1
        max = 100
        if room_no < min or room_no > max:
            return {'error' : f'Hostel rooms must be between {min} and {max} respectively!'},400
        
        price = data['price']
        min = 7000
        max = 30000
        if price < min or price > max:
            return {'error' : f'Room price must be between {min} and {max} price!'},400

        new_room = Rooms(
            room_no = room_no,
            price = price,
            room_type = data['room_type'],
            accommodation_id=data.get('accommodation_id'),
            availability=data['availability'],
            image=data['image'],
            description=data['description']
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
            "room_no": accommodation.room_no,
            "room_type": accommodation.room_type,
            "price": accommodation.price,
            "accommodation_id": accommodation.accommodation_id,
            "image": accommodation.image,
            "availability": accommodation.availability,
            "description": accommodation.description
        }
    
    @jwt_required()
    def patch(self, id):
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return {'error' : 'The user is forbidden from editing the accommodations!'}, 403
        
        data = request.get_json()
        accommodation = Rooms.query.get(id)
        
        if not accommodation:
            return {'message': 'Accommodation not found'}, 404
        
        if 'room_no' in data:
            room = data ['room_no']
            min = 1
            max = 100
            if room < min or room > max:
                return {'error' : f'Hostel rooms must be between {min} and {max} respectively!'},400
            accommodation.room_no = room

        if 'price' in data:
            price = data['price']
            min = 7000
            max = 30000
            if price < min or price > max:
                return {'error' : f'Room price must be between {min} and {max} price!'},400
            accommodation.price = price

        if 'accommodation_id' in data:
            accommodation.accommodation_id = data ['accommodation_id']
        if 'room_type' in data:
            accommodation.room_type = data ['room_type']
        if 'availability' in data:
            accommodation.availability = data ['availability']
        if 'image' in data:
            accommodation.image = data ['image']
        if 'description' in data:
            accommodation.description = data ['description']
        db.session.commit()
        return accommodation.to_dict(), 200
    
    @jwt_required()
    def delete(self, id):
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return {'error' : 'The user is forbidden from deleting the rooms!'}, 403
        
        accommodation = Rooms.query.get(id)
        if not accommodation:
            return {'message': 'room not found!'}, 404
        db.session.delete(accommodation)
        db.session.commit()
        return {'message': 'room deleted successfully!'}
    
class RoomListResource(Resource):
    def get(self):
        accommodation_id = request.args.get('accommodation_id')  # Get accommodation ID from query params
        query = db.session.query(Rooms)

        if accommodation_id:
            query = query.filter(Room.accommodation_id == int(accommodation_id))  # Filter rooms

        rooms = [room.to_dict() for room in query.all()]  # Convert to JSON format
        return {"rooms": rooms}, 200  # Return JSON response
    
class Review(Resource):
    def get (self):
        reviews = Reviews.query.all()
        if not reviews:
            return {"error": "reviews not found"}, 404
        return [accommo.to_dict() for accommo in reviews]
    
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        print("JWT Identity Debug:", current_user)

        if current_user["role"] != "user":
            return {"error": "The user is forbidden from adding new reviews!"}, 403

        data = request.get_json()

        if not data or not all(key in data for key in ("rating", "content")):
            return {"error": "Missing required fields!"}, 422

        try:
            rating = int(data.get("rating"))
            rating = max(1, min(5, rating))
        except ValueError:
            return {"error": "Rating must be a valid number!"}, 400

        new_review = Reviews(
            user_id=current_user["id"],  
            rating=rating,
            content=data["content"],
        )

        db.session.add(new_review)
        db.session.commit()

        return new_review.to_dict(), 201

class MyReview(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        user_reviews = Reviews.query.filter_by(user_id=current_user['id']).all()

        if not user_reviews:
            return {"message": "You have no reviews yet."}, 404

        return [review.to_dict() for review in user_reviews], 200
    
    
class ReviewList(Resource): 
    
    @jwt_required()
    def get(self, id):
        review = Reviews.query.get(id)
        return {
            "id": review.id,
            "rating": review.rating,
            "user_id": review.user_id,
            "content": review.content
        }
    
    @jwt_required()
    def delete(self, id):
        current_user = get_jwt_identity()

        reviews = Reviews.query.get(id)

        if current_user['role'] != 'admin' and reviews.user_id != current_user['id']:
            return {'error': 'You are not authorized to delete this review!'}, 403
        
        if not reviews:
            return {'message': 'reviews not found!'}, 404
        
        db.session.delete(reviews)
        db.session.commit()
        return {'message': 'reviews deleted successfully!'}

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
    
    @jwt_required()
    def post(self):
        current = get_jwt_identity()
        if current['role'] != 'user':
            return {'error' : 'the user is not authorized!'}, 403
        
        data = request.get_json()

        if not data or not all (key in data for key in ('accommodation_id', 'room_id', 'start_date', 'end_date')):
            return {'error': 'Missing required fields!'}, 422
       
        try:
            start_date = datetime.strptime(data['start_date'], "%Y-%m-%d %H:%M") 
            end_date = datetime.strptime(data['end_date'], "%Y-%m-%d %H:%M")
        except ValueError:
            return {'error': 'Invalid date format. Use YYYY-MM-DD HH:MM'}, 400
        
        min_duration = timedelta(days=30)
        if(end_date - start_date) < min_duration:
            return{'error' : 'A booking must be atleast 1 month(30 days)!'}, 400
        
        user_id=current['id']
        accommodation_id=data['accommodation_id']
        room_id=data['room_id']

        room = Rooms.query.get(room_id)
        if not room :
            return {"error": "The room does not exist!"}, 404
        if room.accommodation_id != accommodation_id:
            return {"error": "The room does not belong to the accommodation!"}, 404

        existing_booking = Booking.query.filter(
            Booking.room_id == room.id, 
            Booking.end_date > start_date,
            Booking.start_date < end_date
        ).first()

        if existing_booking:
            return {"error" : "Room is already booked for selected dates!"},400
        
        booking = Booking(
            user_id = user_id,
            accommodation_id = accommodation_id,
            room_id = room.id,
            start_date = start_date,
            end_date = end_date
        )

        db.session.add(booking)
        room.availability = "booked!"
        db.session.commit()
        return booking.to_dict(),201
    
    @jwt_required()
    def delete(self, id):
        current =  get_jwt_identity()

        booking = Booking.query.get(id)
        if not booking:
            return {'message': 'Booking not found!'}, 404
        
        if current['role'] != 'admin' and booking.user_id != current['id']:
            return {'error' : 'the user is not authorized to delete the booking!'}, 403
        
        room = booking.room
        if room:
            room.availability = "available!"

        db.session.delete(booking)
        db.session.commit()
        return {'message': 'Booking canceled successfully!'}, 200

class Bookings(Resource):
    @jwt_required()
    def get(self, id):
        current = get_jwt_identity()
        booking = Booking.query.get(id)
        if not booking:
            return {'message': 'Booking not found!'}, 404
        
        if booking.user_id != current['id'] and current['role'] != 'admin':
            return {'error' : 'the user is not authorized!'}, 403
        
        return {
            'id': booking.id,
            'user_id': booking.user_id,
            'accommodation_id': booking.accommodation_id,
            'room_id': booking.room_id,
            'start_date': booking.start_date,
            'end_date': booking.end_date
        }, 200
    
class RoomBookings(Resource):
    def get(self, room_no):
        bookings = Booking.query.filter_by(room_id=room_no).all()
        if not bookings:
            return {"message": "No bookings found for this room."}, 404

        return [{
            "start_date": booking.start_date.strftime("%Y-%m-%d %H:%M"),
            "end_date": booking.end_date.strftime("%Y-%m-%d %H:%M")
        } for booking in bookings]

