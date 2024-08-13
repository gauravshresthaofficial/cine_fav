from pymongo import MongoClient
from django.conf import settings
import facebook as fb
from datetime import datetime, timedelta
import requests
import os
import logging

logging.basicConfig(filename='post_to_facebook.log', level=logging.INFO)

# Log a message when the script starts
logging.info('Starting the script')

# Constants
ACCESS_TOKEN = "EAAGjWbItBAgBO40meFwAqO39xmUzOfVdPcRlykd2cYS5QRgBujBzyswFnrWcWZCUZBbDGjK8zwvP2ZAIWxB9kc9GCeGZC7k9wgVIi7BZBk0d2Nj7IakRp37TpRJ2eixIZBhLB9EWadD4g3og1yvXWsCFy5gbUZCHX1REu0qHO8wZA69AlYfmSV1v3UnIaXRbuwOYtw0epGJgrue6jZBvYxOsUNv6zBOOKSXZAKT8qxZAXOe"  # Replace with your Page Access Token
MONGO_CONNECTION_STRING = "mongodb+srv://cinefav:cinefav@cluster0.nsbu5lq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "imdbcalendar"
TEMP_IMAGE_PATH = "temp_image.jpg"  # Temporary path to store downloaded image

# Initialize Facebook Graph API
facebook_api = fb.GraphAPI(ACCESS_TOKEN)

# Initialize MongoDB client
mongo_client = MongoClient(MONGO_CONNECTION_STRING)
db = mongo_client[DB_NAME]

def get_week_dates(week_offset=0):
    """Returns the start (Friday) and end (Thursday) dates of the week for a given offset."""
    today = datetime.today().date()
    start_of_current_week = today - timedelta(days=(today.weekday() + 3) % 7)
    start_of_target_week = start_of_current_week + timedelta(weeks=week_offset)
    end_of_target_week = start_of_target_week + timedelta(days=6)
    return start_of_target_week, end_of_target_week

def download_image(image_url, path):
    """Downloads an image from the provided URL and saves it to the specified path."""
    try:
        response = requests.get(image_url)
        response.raise_for_status()  # Raise an error for bad responses
        with open(path, 'wb') as file:
            file.write(response.content)
        print(f"Image downloaded to {path}")
    except Exception as e:
        print(f"Error downloading image: {e}")
        return False
    return True

def post_to_facebook(movie_name, duration, image_path):
    """Posts the movie details with an image to Facebook."""
    message = movie_name
    if duration:  # Add duration only if it's provided
        message += f"\nDuration = {duration}"
    
    try:
        # Open the image file in binary mode
        with open(image_path, 'rb') as image_file:
            # Post to the page feed
            facebook_api.put_photo(image=image_file, message=message)
        print(f"Posted to Facebook: {message}")
    except Exception as e:
        print(f"Error posting to Facebook: {e}")

def update_movie_uploaded_status(collection, movie_id, status=True):
    """Updates the 'uploaded' status of a movie in the MongoDB collection."""
    collection.update_one({'_id': movie_id}, {'$set': {'uploaded': status}})

def get_movies():
    """Retrieve and process movies for the next week."""
    start_date_next_week, _ = get_week_dates(week_offset=1)
    collection_name = f"movies_{start_date_next_week}"
    collection = db[collection_name]
    
    movies = collection.find({})
    done = 0
    
    for movie in movies:
        movie_name = movie.get('title')
        
        # Skip to the next movie if there's no title
        if not movie_name:
            continue

        if not movie.get("uploaded", False):
            duration = movie.get('duration')  # Get duration, could be None
            image_url = movie.get('image_url', None)

            if image_url and download_image(image_url, TEMP_IMAGE_PATH):
                post_to_facebook(movie_name, duration, TEMP_IMAGE_PATH)
                update_movie_uploaded_status(collection, movie['_id'], status=True)
                done = 1
                break
    
    # Clean up temporary image file
    if os.path.exists(TEMP_IMAGE_PATH):
        os.remove(TEMP_IMAGE_PATH)

    if done == 0:
        print("No movie data for this week.")
    print(done)

def main():
    """Main function to be called by the Django management command."""
    logging.info('Running get_movies')
    get_movies()

if __name__ == "__main__":
    main()