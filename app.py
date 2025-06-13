#!/usr/bin/env python3
"""
Ghibli Landscapes API - Flask Server with CORS

This script implements a Flask API that serves random Ghibli landscape images
and ensures the same image is returned for the same ID or query.
"""

import os
import json
import hashlib
import random
from flask import Flask, jsonify, request, redirect, abort, render_template
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
API_VERSION = "1.0.0"
DATABASE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.json")
DEFAULT_PORT = 5001

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins

# Load the database
def load_database():
    """Load the image database from the JSON file."""
    try:
        with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading database: {e}")
        return {"images": [], "film_codes": []}

# Generate a consistent hash for a query string
def generate_query_hash(query):
    return hashlib.sha256(query.encode()).hexdigest()

# Select an image based on a query hash
def select_image_by_hash(query_hash, database):
    if not database["images"]:
        return None
    hash_int = int(query_hash, 16)
    index = hash_int % len(database["images"])
    return database["images"][index]

# Initialize the database
database = load_database()
logger.info(f"Loaded database with {len(database['images'])} images")

@app.route('/')
def index():
    random_image = random.choice(database["images"]) if database["images"] else None
    sample_images = random.sample(database["images"], min(6, len(database["images"]))) if database["images"] else []
    return render_template('index.html',
                           image_count=len(database["images"]),
                           film_codes=database["film_codes"],
                           random_image=random_image,
                           sample_images=sample_images)

@app.route('/api')
def api_docs():
    return render_template('api.html')

@app.route('/api/random')
def random_image():
    if not database["images"]:
        return jsonify({"error": "No images available"}), 404
    image = random.choice(database["images"])
    return jsonify(image)

@app.route('/api/image')
def get_image():
    image_id = request.args.get('id')
    query = request.args.get('q')

    if not image_id and not query:
        return jsonify({"error": "Missing required parameter: 'id' or 'q'"}), 400

    if image_id:
        for image in database["images"]:
            if image["id"] == image_id:
                return jsonify(image)
        return jsonify({"error": f"Image with ID '{image_id}' not found"}), 404
    else:
        query_hash = generate_query_hash(query)
        image = select_image_by_hash(query_hash, database)
        if not image:
            return jsonify({"error": "No images available"}), 404
        image["query"] = query
        image["query_hash"] = query_hash
        return jsonify(image)

@app.route('/api/films')
def list_films():
    return jsonify({"film_codes": database["film_codes"]})

@app.route('/api/film/<film_code>')
def film_image(film_code):
    film_images = [img for img in database["images"] if img["film_code"] == film_code]
    if not film_images:
        return jsonify({"error": f"No images found for film '{film_code}'"}), 404
    return jsonify(random.choice(film_images))

@app.route('/api/redirect/random')
def redirect_random():
    if not database["images"]:
        abort(404)
    return redirect(random.choice(database["images"])["url"])

@app.route('/api/redirect')
def redirect_image():
    image_id = request.args.get('id')
    query = request.args.get('q')

    if not image_id and not query:
        return jsonify({"error": "Missing required parameter: 'id' or 'q'"}), 400

    if image_id:
        for image in database["images"]:
            if image["id"] == image_id:
                return redirect(image["url"])
        abort(404)
    else:
        query_hash = generate_query_hash(query)
        image = select_image_by_hash(query_hash, database)
        if not image:
            abort(404)
        return redirect(image["url"])

if __name__ == "__main__":
    database = load_database()
    logger.info(f"Starting Ghibli Landscapes API with {len(database['images'])} images")
    app.run(host='0.0.0.0', port=DEFAULT_PORT, debug=True)
