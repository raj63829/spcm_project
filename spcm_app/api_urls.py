"""
API URL patterns for SPCM app
"""
#Developed By RAJ SHARMA
from django.urls import path
from . import views

urlpatterns = [
    path('stock/<str:symbol>/', views.api_stock_data, name='api_stock_data'),
]
