from flask import Flask, jsonify
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flasgger import Swagger

import os
from dotenv import load_dotenv
from routes.recipeRoute import recipe_routes
from routes.registerRoute import register_routes

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Load configuration from .env file
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Initialize extensions
mongo = PyMongo(app)  # Create an instance of PyMongo
bcrypt = Bcrypt(app)  # Initialize Bcrypt
jwt = JWTManager(app)  # Initialize JWT Manager
swagger = Swagger(app)



# Test MongoDB connection
@app.route('/test_db_connection', methods=['GET'])
def test_db_connection():
    try:
        # Attempt to list collections to test the connection
        collections = mongo.db.list_collection_names()
        return jsonify({"message": "MongoDB connection successful!", "collections": collections}), 200
    except Exception as e:
        return jsonify({"message": "MongoDB connection failed!", "error": str(e)}), 500

# Register routes
register_routes(app,mongo)

recipe_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
