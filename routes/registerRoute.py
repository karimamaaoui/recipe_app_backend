from flask import request, jsonify
import jwt
import datetime
from flask_bcrypt import Bcrypt

from models.userModel import User

bcrypt = Bcrypt()  # Initialize Bcrypt

def register_routes(app,mongo):
    @app.route('/')
    def home():
        return "Welcome to the Flask JWT Auth API!"

    # Register User
    @app.route('/register', methods=['POST'])
    def register():
        """Register a new user.
        ---
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                username:
                  type: string
                  example: testuser
                  
                email:
                  type: string
                  example: testuser@example.com
                password:
                  type: string
                  example: testpass
        responses:
          201:
            description: User registered successfully
          400:
            description: User already exists
        """
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        
        if(not email  or not username or not password):
          return {'error': 'All fields (username, email, password) are required'}, 400


            # Check if the email or username already exists
        if mongo.db.users.find_one({'$or': [{'email': email}, {'username': username}]}):
          return jsonify({"message": "Email or Username already exists"}), 400
        
        new_user = User.create_user(mongo, username,email, password)  
        if not new_user:
            return jsonify({"message": "Error Creating User"}), 500

        return jsonify({"message": "User registered successfully!"}), 201


    # Login User
    @app.route('/login', methods=['POST'])
    def login():
        """Login a user.
        ---
        parameters:
          - name: bodya
            in: body
            required: true
            schema:
              type: object
              properties:
                username:
                  type: string
                  example: testuser
                password:
                  type: string
                  example: testpass
        responses:
          200:
            description: Token generated successfully
          401:
            description: Invalid credentials
        """
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.find_user(mongo, username)
        if user and bcrypt.check_password_hash(user['password'], password):
            # Generate JWT token with user ID as the subject
            token = jwt.encode({
                'sub': str(user['_id']),  # Use user ID for the subject claim
                'username': username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)  # Token valid for 30 mins
            }, app.config['SECRET_KEY'], algorithm='HS256')

            return jsonify({'token': token}), 200
        
        return jsonify({"message": "Invalid credentials"}), 401