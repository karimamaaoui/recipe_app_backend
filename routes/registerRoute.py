from flask import request, jsonify
import jwt
import datetime
from flask_bcrypt import Bcrypt
from models.userModel import User

bcrypt = Bcrypt()  # Initialize Bcrypt

def register_routes(app, mongo):
    @app.route('/')
    def home():
        return "Welcome to the Flask JWT Auth API!"

    # Register User
    @app.route('/register', methods=['POST'])
    def register():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        if not email or not username or not password:
            return jsonify({'error': 'All fields (username, email, password) are required'}), 400

        if mongo.db.users.find_one({'$or': [{'email': email}, {'username': username}]}):
            return jsonify({"message": "Email or Username already exists"}), 400
        
        new_user = User.create_user(mongo, username, email, password)  
        if not new_user:
            return jsonify({"message": "Error Creating User"}), 500

        return jsonify({"message": "User registered successfully!"}), 201


    # Login User
    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = mongo.db.users.find_one({'email': email})  # Find user by email
        if user and bcrypt.check_password_hash(user['password'], password):
            token = jwt.encode({
                'sub': str(user['_id']),
                'username': user['username'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            }, app.config['SECRET_KEY'], algorithm='HS256')

            return jsonify({'token': token}), 200
        
        return jsonify({"message": "Invalid credentials"}), 401