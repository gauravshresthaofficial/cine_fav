from django.urls import path
from .views import get_movies

urlpatterns = [
    path('movies/', get_movies, name='get_movies'),
]
