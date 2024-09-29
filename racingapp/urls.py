from django.urls import path
from .views import race_selection_view, logout_view

urlpatterns = [
    path('', race_selection_view, name='racing_silks'),
    path('logout/', logout_view, name='logout'),
]
