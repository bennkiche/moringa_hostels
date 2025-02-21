from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from models import db
from flask_cors import CORS
# import os
from resources.hostels import Accommodation,AccommodationList,Users,Payments,PaymentsList,Bookings,BookingsList
# from dotenv import load_dotenv
# load_dotenv()

app =Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hostel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)
CORS(app, supports_credentials=True)
api = Api(app)

# with app.app_context():
#     db.create_all()

@app.route('/')
def home():
    return '<h1>Welcome to Moringa Hostels!</h1>'
    
api.add_resource(AccommodationList, '/accommodation')
api.add_resource(Accommodation, '/accommodation/<int:id>')

api.add_resource(Users, '/users/<int:id>')

# api.add_resource(PaymentsList, '/payments')
# api.add_resource(Payments, '/payments/<int:id>')

api.add_resource(BookingsList, '/bookings', '/bookings/<int:id>' )
api.add_resource(Bookings, '/bookings/<int:id>')

if __name__ == '__main__':
    app.run(debug=True)