#!/usr/bin/env python3
"""
Ghibli Landscapes API - Test Script

This script tests the API for consistency and randomness.
"""

import requests
import json
import time
import sys

# Constants
API_BASE_URL = "http://localhost:5000"
TEST_QUERIES = [
    "totoro",
    "spirited away",
    "castle in the sky",
    "howl's moving castle",
    "princess mononoke",
    "nausicaa",
    "kiki's delivery service",
    "my neighbor totoro",
    "ponyo",
    "ghibli landscapes"
]

def test_random_endpoint():
    """Test the random endpoint for variety."""
    print("\n=== Testing Random Endpoint ===")
    
    # Make multiple requests and check if we get different images
    image_ids = set()
    for i in range(10):
        try:
            response = requests.get(f"{API_BASE_URL}/api/random")
            response.raise_for_status()
            data = response.json()
            
            image_id = data.get("id")
            if not image_id:
                print(f"Error: Missing image ID in response: {data}")
                continue
                
            image_ids.add(image_id)
            print(f"Random request {i+1}: Got image ID {image_id} from {data.get('film_code', 'unknown')}")
            
        except Exception as e:
            print(f"Error testing random endpoint: {e}")
    
    # Check if we got different images
    unique_count = len(image_ids)
    print(f"\nGot {unique_count} unique images out of 10 requests")
    if unique_count > 1:
        print("✅ Random endpoint returns varied images")
    else:
        print("❌ Random endpoint may not be returning varied images")

def test_consistency():
    """Test that the same query returns the same image."""
    print("\n=== Testing Consistency ===")
    
    results = {}
    
    # First round of requests
    print("\nFirst round of requests:")
    for query in TEST_QUERIES:
        try:
            response = requests.get(f"{API_BASE_URL}/api/image", params={"q": query})
            response.raise_for_status()
            data = response.json()
            
            image_id = data.get("id")
            if not image_id:
                print(f"Error: Missing image ID in response for query '{query}': {data}")
                continue
                
            results[query] = image_id
            print(f"Query '{query}': Got image ID {image_id} from {data.get('film_code', 'unknown')}")
            
        except Exception as e:
            print(f"Error testing consistency for query '{query}': {e}")
    
    # Wait a moment
    print("\nWaiting before second round...")
    time.sleep(2)
    
    # Second round of requests to check consistency
    print("\nSecond round of requests:")
    all_consistent = True
    
    for query in TEST_QUERIES:
        if query not in results:
            continue
            
        try:
            response = requests.get(f"{API_BASE_URL}/api/image", params={"q": query})
            response.raise_for_status()
            data = response.json()
            
            image_id = data.get("id")
            if not image_id:
                print(f"Error: Missing image ID in response for query '{query}': {data}")
                all_consistent = False
                continue
                
            if image_id == results[query]:
                print(f"Query '{query}': ✅ Consistent! Got same image ID {image_id}")
            else:
                print(f"Query '{query}': ❌ Inconsistent! Got {image_id}, expected {results[query]}")
                all_consistent = False
            
        except Exception as e:
            print(f"Error testing consistency for query '{query}': {e}")
            all_consistent = False
    
    if all_consistent:
        print("\n✅ All queries returned consistent results!")
    else:
        print("\n❌ Some queries returned inconsistent results!")

def test_film_endpoint():
    """Test the film endpoint."""
    print("\n=== Testing Film Endpoint ===")
    
    try:
        # Get list of films
        response = requests.get(f"{API_BASE_URL}/api/films")
        response.raise_for_status()
        data = response.json()
        
        film_codes = data.get("film_codes", [])
        if not film_codes:
            print("Error: No film codes returned")
            return
            
        print(f"Got {len(film_codes)} film codes")
        
        # Test a few film codes
        for film_code in film_codes[:3]:  # Test first 3 films
            response = requests.get(f"{API_BASE_URL}/api/film/{film_code}")
            response.raise_for_status()
            data = response.json()
            
            image_id = data.get("id")
            if not image_id:
                print(f"Error: Missing image ID in response for film '{film_code}': {data}")
                continue
                
            print(f"Film '{film_code}': Got image ID {image_id}")
        
        print("✅ Film endpoint working correctly")
        
    except Exception as e:
        print(f"Error testing film endpoint: {e}")

def test_error_handling():
    """Test error handling."""
    print("\n=== Testing Error Handling ===")
    
    test_cases = [
        {"endpoint": "/api/image", "params": {}, "expected_status": 400, "description": "Missing required parameters"},
        {"endpoint": "/api/image", "params": {"id": "nonexistent"}, "expected_status": 404, "description": "Nonexistent ID"},
        {"endpoint": "/api/film/nonexistent", "params": {}, "expected_status": 404, "description": "Nonexistent film code"}
    ]
    
    for test_case in test_cases:
        try:
            response = requests.get(f"{API_BASE_URL}{test_case['endpoint']}", params=test_case['params'])
            
            if response.status_code == test_case["expected_status"]:
                print(f"✅ {test_case['description']}: Got expected status {response.status_code}")
            else:
                print(f"❌ {test_case['description']}: Got status {response.status_code}, expected {test_case['expected_status']}")
                
        except Exception as e:
            print(f"Error testing {test_case['description']}: {e}")

def main():
    """Run all tests."""
    print("Starting Ghibli Landscapes API tests...")
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL}/")
        response.raise_for_status()
        print("API is running!")
        
        # Run tests
        test_random_endpoint()
        test_consistency()
        test_film_endpoint()
        test_error_handling()
        
        print("\n=== Test Summary ===")
        print("All tests completed. Check the results above for any issues.")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure it's running on http://localhost:5000")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
