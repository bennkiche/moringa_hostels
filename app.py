from flask import Flask, request
from flask_migrate import Migrate
from flask_cors import CORS
import os
import re
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask_restful import Resource, Api
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from resources.crude import Accommodation,AccommodationList,Users,Bookings,BookingsList, Room, RoomList
from models import db, User, Accommodations

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

db.init_app(app)
migrate = Migrate(app,db)
CORS(app, supports_credentials=True)
api = Api(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

@app.route('/')
def index():
    return 'Welcome to the home page!'

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_strong_password(password):
    return re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}$", password)

class Signup(Resource):
    def post(self):
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'user')

        if not is_valid_email(email):
            return {'error': 'Invalid email format, please provide a valid email address.'}, 400
        
        if User.query.filter_by(email=email).first():
            return{'error' : 'Email already exists!'}, 400
        
        if not is_strong_password(password):
            return {'error': 'Password must be at least 8 characters long and contain both letters and numbers.'}, 400
        
        hash = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(name=name, email=email, password = hash, role = role)
        db.session.add(new_user)
        db.session.commit()
        return{'message' : 'User created succesfully!'}, 201
    
class Login(Resource):
    def post(self):
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'user')

        user = User.query.filter_by(name=name, email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            create_token = create_access_token(identity={'id':user.id, 'name':user.name, 'email':user.email, 'role':user.role})
            refresh_token = create_refresh_token(identity={'id':user.id, 'name':user.name, 'email':user.email, 'role':user.role})
            return {'create_token':create_token, 'refresh_token':refresh_token, 'role':user.role, 'user': user.to_dict()}
        return {'error' : 'Incorrect name, email or password, please try again!'}, 401

class DeleteAcc(Resource):
    @jwt_required()
    def delete(self):
        current = get_jwt_identity()
        current_user = current.get('id')
        delete_user = User.query.get(current_user)
        if not delete_user:
            return{'error' : 'the user does not exist!'}, 404
        db.session.delete(delete_user)
        db.session.commit()
        return {'message' : 'the user was deleted successfully!'}, 200
    
class Refresh(Resource):
    @jwt_required(refresh = True)
    def post(self):
        current_user = get_jwt_identity()
        new_access_token = create_refresh_token(identity = current_user)
        return{'access_token':new_access_token}, 201
    
class Accommodate(Resource):
    @jwt_required()
    def get(self):
        accommodations = Accommodations.query.all()
        return[{'id':acom.id, 'name':acom.name,'user_id':acom.user_id, 'price':acom.price, 'image':acom.image,'description':acom.description, 'availability':acom.availability} for acom in accommodations]

class Use(Resource):
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return {'error' : 'The user is forbidded!'}, 403
        user = User.query.all()
        return[{'id':acom.id,'name':acom.name, 'email':acom.email, 'role':acom.role} for acom in user]

api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(Refresh, '/refresh')
api.add_resource(DeleteAcc, '/delete')
api.add_resource(Accommodate, '/accommodate')
api.add_resource(Use, '/users')

api.add_resource(AccommodationList, '/accommodations')
api.add_resource(Accommodation, '/accommodations/<int:id>')

api.add_resource(Room, '/rooms')
api.add_resource(RoomList, '/rooms/<int:id>')

api.add_resource(Users, '/users/<int:id>')

api.add_resource(BookingsList, '/bookings', '/bookings/<int:id>' )
api.add_resource(Bookings, '/bookings/<int:id>')

if __name__ == '__main__':
    app.run(debug=True)