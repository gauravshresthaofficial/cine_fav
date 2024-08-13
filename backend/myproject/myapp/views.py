from rest_framework.decorators import api_view
from rest_framework.response import Response
from pymongo import MongoClient
from django.conf import settings

# MongoDB connection
client = MongoClient("mongodb+srv://cinefav:cinefav@cluster0.nsbu5lq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['imdbcalendar']

@api_view(['GET'])
def get_movies(request):
    """API endpoint to retrieve movies from MongoDB."""
    week_start = request.query_params.get('week_start')  # Expecting date in 'YYYY-MM-DD' format

    if week_start:
        collection_name = f"movies_{week_start}"
        collection = db[collection_name]
        movies = list(collection.find({}, {'_id': 0}))  # Exclude MongoDB's _id field from the response
    else:
        return Response({"error": "week_start parameter is required"}, status=400)

    if not movies:
        return Response({"message": "No movies found"}, status=404)

    return Response(movies, status=200)
