from django.urls import path
from .views import home

app_name = 'data'

urlpatterns = [
    path('script/', home, name="home"),
]
