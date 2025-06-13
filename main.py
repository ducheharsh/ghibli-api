#!/usr/bin/env python3
"""
Ghibli Landscapes API - Main Flask Application

This script implements a Flask API that serves random Ghibli landscape images
and ensures the same image is returned for the same ID or query.
"""

import os
import json
import hashlib
import random
import sys
import logging
from flask import Flask, jsonify, request, redirect, abort, render_template
from flask_cors import CORS          # NEW: enable Cross‑Origin Resource Sharing (CORS)

# Configure path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Constants
API_VERSION = "1.0.0"
DATABASE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.json")

# Initialize Flask app
app = Flask(__name__)
CORS(app)                            # NEW: allows requests from any origin (adjust as needed)

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------
def load_database():
    """Load the image database from the JSON file."""
    try:
        with open(DATABASE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading database: {e}")
        # Return an empty database as fallback
        return {"images": [], "film_codes": []}


def generate_query_hash(query: str) -> str:
    """Generate a consistent hash for a query string."""
    return hashlib.sha256(query.encode()).hexdigest()


def select_image_by_hash(query_hash: str, database: dict):
    """Select an image deterministically based on a query hash."""
    if not database["images"]:
        return None
    hash_int = int(query_hash, 16)
    image_index = hash_int % len(database["images"])
    return database["images"][image_index]


# -----------------------------------------------------------------------------
# Load the database at startup
# -----------------------------------------------------------------------------
database = load_database()
logger.info(f"Loaded database with {len(database['images'])} images")

# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@app.route("/")
def index():
    """Website home page."""
    random_image = random.choice(database["images"]) if database["images"] else None
    sample_images = (
        random.sample(database["images"], min(9, len(database["images"])))
        if database["images"]
        else []
    )
    return render_template(
        "index.html",
        random_image=random_image,
        sample_images=sample_images,
        film_codes=database["film_codes"],
        image_count=len(database["images"]),
    )


@app.route("/api")
def api_docs():
    """API documentation page."""
    return render_template(
        "api.html",
        api_version=API_VERSION,
        image_count=len(database["images"]),
        film_count=len(database["film_codes"]),
    )


@app.route("/api/random")
def random_image():
    """Return a random landscape image."""
    if not database["images"]:
        return jsonify({"error": "No images available"}), 404
    image = random.choice(database["images"])
    return jsonify(image)


@app.route("/api/image")
def get_image():
    """Return an image by ID or query."""
    image_id = request.args.get("id")
    query = request.args.get("q")
    if not image_id and not query:
        return jsonify({"error": "Missing required parameter: 'id' or 'q'"}), 400

    if image_id:
        # Find by ID
        for img in database["images"]:
            if img["id"] == image_id:
                return jsonify(img)
        return jsonify({"error": f"Image with ID '{image_id}' not found"}), 404

    # Find by query
    query_hash = generate_query_hash(query)
    img = select_image_by_hash(query_hash, database)
    if not img:
        return jsonify({"error": "No images available"}), 404
    return jsonify({**img, "query": query, "query_hash": query_hash})


@app.route("/api/films")
def list_films():
    """List all available film codes."""
    return jsonify({"film_codes": database["film_codes"]})


@app.route("/api/film/<film_code>")
def film_image(film_code):
    """Return a random image from a specific film."""
    film_images = [img for img in database["images"] if img["film_code"] == film_code]
    if not film_images:
        return jsonify({"error": f"No images found for film '{film_code}'"}), 404
    return jsonify(random.choice(film_images))


@app.route("/api/redirect/random")
def redirect_random():
    """Redirect to a random image URL."""
    if not database["images"]:
        abort(404)
    return redirect(random.choice(database["images"])["url"])


@app.route("/api/redirect")
def redirect_image():
    """Redirect to an image URL by ID or query."""
    image_id = request.args.get("id")
    query = request.args.get("q")
    if not image_id and not query:
        return jsonify({"error": "Missing required parameter: 'id' or 'q'"}), 400

    if image_id:
        for img in database["images"]:
            if img["id"] == image_id:
                return redirect(img["url"])
        abort(404)

    query_hash = generate_query_hash(query)
    img = select_image_by_hash(query_hash, database)
    if not img:
        abort(404)
    return redirect(img["url"])


# -----------------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Reload database on startup (redundant but explicit)
    database = load_database()
    logger.info(f"Starting Ghibli Landscapes API with {len(database['images'])} images")
    app.run(host="0.0.0.0", port=5000, debug=True)
