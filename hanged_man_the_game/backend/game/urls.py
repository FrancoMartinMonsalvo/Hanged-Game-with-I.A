from django.urls import path
from .views import index  # Import the view

urlpatterns = [
    path('', index, name='my_endpoint'),
]