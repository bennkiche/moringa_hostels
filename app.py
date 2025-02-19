from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from models import db
from flask_cors import CORS
# import os
from resources.hostels import Accommodation,AccommodationList,Users,UsersList,Payments,PaymentsList,Bookings,BookingsList,Password_reset,Password_resetList,Student_verification,Student_verificationList
# from dotenv import load_dotenv
# load_dotenv()

app =Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hostel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)
CORS(app, supports_credentials=True)
api = Api(app)

@app.route('/')
def home():
    return '<h1>Welcome to Moringa Hostels!</h1>'
    
api.add_resource(Accommodation, '/accommodation')
api.add_resource(AccommodationList, '/accommodation/<int:id>')

api.add_resource(Student_verification, '/student_verification')
api.add_resource(Student_verificationList, '/student_verification/<int:id>')

api.add_resource(Users, '/users')
api.add_resource(UsersList, '/users/<int:id>')

api.add_resource(Payments, '/payments')
api.add_resource(PaymentsList, '/payments/<int:id>')

api.add_resource(Bookings, '/bookings')
api.add_resource(BookingsList, '/bookings/<int:id>')

api.add_resource(Password_reset, '/password_reset')
api.add_resource(Password_resetList, '/password_reset/<int:id>')

if __name__ == '__main__':
    app.run(debug=True)