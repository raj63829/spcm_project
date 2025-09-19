"""
URL patterns for SPCM app - Enhanced with Authentication
"""
from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.dashboard, name='dashboard'),
    path('stock/<str:symbol>/', views.stock_analysis, name='stock_analysis'),
    path('stock/<str:symbol>/news/', views.news_analysis, name='news_analysis'),
    path('stock/<str:symbol>/refresh/', views.refresh_stock_data, name='refresh_stock_data'),
    path('search/', views.stock_search, name='stock_search'),
    path('market/', views.market_overview, name='market_overview'),
    
    # Authentication
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    
    # Portfolio management
    path('portfolios/', views.portfolio_list, name='portfolio_list'),
    path('portfolios/create/', views.create_portfolio, name='create_portfolio'),
    path('portfolios/<int:portfolio_id>/', views.portfolio_detail, name='portfolio_detail'),
    path('portfolios/<int:portfolio_id>/add-position/', views.add_position, name='add_position'),
    path('portfolios/<int:portfolio_id>/delete/', views.delete_portfolio, name='delete_portfolio'),
]
