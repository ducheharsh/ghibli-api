#!/usr/bin/env python3
"""
Ghibli Landscapes API - Flask Server

This script implements a Flask API that serves random Ghibli landscape images
and ensures the same image is returned for the same ID or query.
"""

import os
import json
import hashlib
import random
from flask import Flask, jsonify, request, redirect, abort, render_template
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
API_VERSION = "1.0.0"
DATABASE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.json")
DEFAULT_PORT = 5000

# Initialize Flask app
app = Flask(__name__)

# Load the database
def load_database():
    """Load the image database from the JSON file."""
    try:
        with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading database: {e}")
        # Return an empty database as fallback
        return {"images": [], "film_codes": []}

# Generate a consistent hash for a query string
def generate_query_hash(query):
    """Generate a consistent hash for a query string."""
    return hashlib.sha256(query.encode()).hexdigest()

# Select an image based on a query hash
def select_image_by_hash(query_hash, database):
    """Select an image based on a query hash."""
    if not database["images"]:
        return None
    
    # Use the hash to deterministically select an image
    # This ensures the same query always returns the same image
    hash_int = int(query_hash, 16)
    image_index = hash_int % len(database["images"])
    return database["images"][image_index]

# Initialize the database
database = load_database()
logger.info(f"Loaded database with {len(database['images'])} images")

@app.route('/')
def index():
    """Serve the main page."""
    random_image = random.choice(database["images"]) if database["images"] else None
    sample_images = random.sample(database["images"], min(6, len(database["images"]))) if database["images"] else []
    return render_template('index.html',
                         image_count=len(database["images"]),
                         film_codes=database["film_codes"],
                         random_image=random_image,
                         sample_images=sample_images)

@app.route('/api')
def api_docs():
    """Serve the API documentation page."""
    return render_template('api.html')

@app.route('/api/random')
def random_image():
    """Return a random landscape image."""
    if not database["images"]:
        return jsonify({"error": "No images available"}), 404
    
    image = random.choice(database["images"])
    return jsonify({
        "id": image["id"],
        "url": image["url"],
        "film_code": image["film_code"],
        "film_name": image["film_name"],
        "image_number": image["image_number"]
    })

@app.route('/api/image')
def get_image():
    """Return an image by ID or query."""
    image_id = request.args.get('id')
    query = request.args.get('q')
    
    if not image_id and not query:
        return jsonify({"error": "Missing required parameter: 'id' or 'q'"}), 400
    
    if image_id:
        # Find image by ID
        for image in database["images"]:
            if image["id"] == image_id:
                return jsonify({
                    "id": image["id"],
                    "url": image["url"],
                    "film_code": image["film_code"],
                    "film_name": image["film_name"],
                    "image_number": image["image_number"]
                })
        return jsonify({"error": f"Image with ID '{image_id}' not found"}), 404
    
    else:
        # Find image by query
        query_hash = generate_query_hash(query)
        image = select_image_by_hash(query_hash, database)
        
        if not image:
            return jsonify({"error": "No images available"}), 404
        
        return jsonify({
            "id": image["id"],
            "url": image["url"],
            "film_code": image["film_code"],
            "film_name": image["film_name"],
            "image_number": image["image_number"],
            "query": query,
            "query_hash": query_hash
        })

@app.route('/api/films')
def list_films():
    """List all available film codes."""
    return jsonify({
        "film_codes": database["film_codes"]
    })

@app.route('/api/film/<film_code>')
def film_image(film_code):
    """Return a random image from a specific film."""
    # Filter images by film code
    film_images = [img for img in database["images"] if img["film_code"] == film_code]
    
    if not film_images:
        return jsonify({"error": f"No images found for film '{film_code}'"}), 404
    
    image = random.choice(film_images)
    return jsonify({
        "id": image["id"],
        "url": image["url"],
        "film_code": image["film_code"],
        "film_name": image["film_name"],
        "image_number": image["image_number"]
    })

@app.route('/api/redirect/random')
def redirect_random():
    """Redirect to a random image."""
    if not database["images"]:
        abort(404)
    
    image = random.choice(database["images"])
    return redirect(image["url"])

@app.route('/api/redirect')
def redirect_image():
    """Redirect to an image by ID or query."""
    image_id = request.args.get('id')
    query = request.args.get('q')
    
    if not image_id and not query:
        return jsonify({"error": "Missing required parameter: 'id' or 'q'"}), 400
    
    if image_id:
        # Find image by ID
        for image in database["images"]:
            if image["id"] == image_id:
                return redirect(image["url"])
        abort(404)
    
    else:
        # Find image by query
        query_hash = generate_query_hash(query)
        image = select_image_by_hash(query_hash, database)
        
        if not image:
            abort(404)
        
        return redirect(image["url"])

if __name__ == "__main__":
    # Reload the database on startup
    database = load_database()
    logger.info(f"Starting Ghibli Landscapes API with {len(database['images'])} images")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=DEFAULT_PORT, debug=True)
