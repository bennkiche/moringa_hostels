from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from flask_migrate import Migrate
from flask_cors import CORS
import os
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask_restful import Resource, Api
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from resources.hostels import Accommodation,AccommodationList,Users,Payments,PaymentsList,Bookings,BookingsList

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

db = SQLAlchemy(app)
migrate = Migrate(app,db)
CORS(app, supports_credentials=True)
api = Api(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

@app.route('/')
def index():
    return 'Welcome to the home page!'

class User(db.Model, SerializerMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False, unique = True)
    email = db.Column(db.String, nullable = False, unique = True)
    password = db.Column(db.String, nullable = False)
    role = db.Column(db.String, nullable = False, default = 'user')

class Signup(Resource):
    def post(self):
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'user')

        if "@gmail.com" not in email:
            return {'error' : 'Invalid email format, email must contaion "@" symbol'}, 400
        if User.query.filter_by(name=name, email=email).first():
            return{'error' : 'Name or email already exists!'}, 400
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
            create_token = create_access_token(identity={'name':user.name, 'email':user.email, 'role':user.role})
            refresh_token = create_refresh_token(identity={'name':user.name, 'email':user.email, 'role':user.role})
            return {'create_token':create_token, 'refresh_token':refresh_token, 'role':user.role}
        return {'error' : 'Incorrect name, email or password, please try again!'}, 401
    
class Refresh(Resource):
    @jwt_required(refresh = True)
    def post(self):
        current_user = get_jwt_identity()
        new_access_token = create_refresh_token(identity = current_user)
        return{'access_token':new_access_token}, 201
    
class Accommodation(Resource):
    @jwt_required()
    def get(self):
        accommodations = Accommodations.query.all()
        return[{'id':acom.id, 'name':acom.name, 'price':acom.price, 'image':acom.image,'description':acom.description, 'availability':acom.availability} for acom in accommodations]

class Users(Resource):
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return {'error' : 'The user is forbidded!'}, 403
        user = User.query.all()
        return[{'id':acom.id,'name':acom.name, 'email':acom.email} for acom in user]

api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(Refresh, '/refresh')
api.add_resource(Accommodation, '/accomodations')
api.add_resource(User, '/users')

api.add_resource(AccommodationList, '/accommodation')
api.add_resource(Accommodation, '/accommodation/<int:id>')

api.add_resource(Users, '/users/<int:id>')

api.add_resource(BookingsList, '/bookings', '/bookings/<int:id>' )
api.add_resource(Bookings, '/bookings/<int:id>')

if __name__ == '__main__':
    app.run(debug=True)