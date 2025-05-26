# Ghibli Landscapes API Documentation

## Overview
This API provides random Studio Ghibli landscape images from the official Ghibli website. It ensures that the same image is returned for the same ID or query, making it consistent across requests.

## Features
- Random Ghibli landscape images
- Consistent image selection based on query or ID
- Film-specific image retrieval
- Direct image redirects

## API Endpoints

### Home
- **URL**: `/`
- **Method**: GET
- **Description**: Returns API information and available endpoints
- **Response**: JSON with API details

### Random Image
- **URL**: `/api/random`
- **Method**: GET
- **Description**: Returns a random Ghibli landscape image
- **Response**: JSON with image details

### Image by ID or Query
- **URL**: `/api/image`
- **Method**: GET
- **Parameters**:
  - `id` (optional): Specific image ID
  - `q` (optional): Query string (same query always returns same image)
- **Description**: Returns an image based on ID or query
- **Response**: JSON with image details

### List Films
- **URL**: `/api/films`
- **Method**: GET
- **Description**: Lists all available film codes
- **Response**: JSON with film codes

### Film-specific Image
- **URL**: `/api/film/<film_code>`
- **Method**: GET
- **Parameters**:
  - `film_code`: Code of the film (e.g., "totoro", "chihiro")
- **Description**: Returns a random image from a specific film
- **Response**: JSON with image details

### Direct Image Redirects
- **URL**: `/api/redirect/random`
- **Method**: GET
- **Description**: Redirects to a random image
- **Response**: HTTP redirect to image URL

- **URL**: `/api/redirect`
- **Method**: GET
- **Parameters**:
  - `id` (optional): Specific image ID
  - `q` (optional): Query string
- **Description**: Redirects to an image based on ID or query
- **Response**: HTTP redirect to image URL

## Response Format
```json
{
  "id": "abcdef1234567890",
  "url": "https://www.ghibli.jp/gallery/totoro001.jpg",
  "film_code": "totoro",
  "film_name": "totoro",
  "image_number": "001"
}
```

## Setup and Deployment

### Requirements
- Python 3.6+
- Flask

### Installation
1. Clone the repository
2. Install dependencies: `pip install flask requests beautifulsoup4`
3. Run the scraper to collect images: `python scraper.py`
4. Start the API server: `python app.py`

### Testing
Run the test script to verify API functionality:
```
python test_api.py
```

## Notes
- The API uses a deterministic hashing algorithm to ensure the same query always returns the same image
- Images are sourced from the official Studio Ghibli website
- The database contains approximately 1,200 images from various Ghibli films
