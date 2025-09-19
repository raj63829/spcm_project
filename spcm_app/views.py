"""
SPCM Django Views - Enhanced with Authentication
"""
#Developed By RAJ SHARMA
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Avg
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import CreateView
from datetime import datetime, timedelta
import json
from django.shortcuts import render, get_object_or_404
from .models import Stock

from .models import (
    Stock, StockPrice, TechnicalIndicator, NewsArticle, 
    SentimentData, StockRecommendation, Portfolio, PortfolioPosition, UserProfile
)
from .forms import (
    StockSearchForm, PortfolioForm, PositionForm, CustomUserCreationForm,
    CustomAuthenticationForm, UserProfileForm, UserUpdateForm
)
from .services import StockDataService, SentimentAnalysisService, RecommendationService, NewsService
from django.db import models

def dashboard(request):
    """Main dashboard view"""
    # Get popular stocks
    popular_stocks = Stock.objects.filter(is_active=True).order_by('-market_cap')[:10]
    
    # Get recent recommendations
    recent_recommendations = StockRecommendation.objects.select_related('stock')[:5]
    
    # Get market sentiment overview
    today = timezone.now().date()
    sentiment_data = SentimentData.objects.filter(date=today).aggregate(
        avg_sentiment=Avg('overall_sentiment')
    )
    
    # Get user-specific data if authenticated
    user_portfolios = None
    if request.user.is_authenticated:
        user_portfolios = Portfolio.objects.filter(user=request.user, is_active=True)[:3]
    
    context = {
        'popular_stocks': popular_stocks,
        'recent_recommendations': recent_recommendations,
        'market_sentiment': sentiment_data.get('avg_sentiment', 0) or 0,
        'search_form': StockSearchForm(),
        'user_portfolios': user_portfolios,
    }
    
    return render(request, 'spcm_app/dashboard.html', context)
#Developed By RAJ SHARMA
def stock_analysis(request, symbol):
    """Detailed stock analysis view with enhanced error handling"""
    symbol = symbol.upper()
    
    # Try to get existing stock or fetch new data
    try:
        stock = Stock.objects.get(symbol=symbol)
        # Check if we have recent data
        latest_price = stock.prices.first()
        if not latest_price or (timezone.now().date() - latest_price.date).days > 7:
            # Data is stale, try to refresh
            try:
                stock_service = StockDataService()
                stock_service.fetch_historical_data(symbol)
                stock_service.calculate_technical_indicators(symbol)
                
                news_service = NewsService()
                news_service.fetch_stock_news(symbol)
                
                sentiment_service = SentimentAnalysisService()
                sentiment_service.calculate_daily_sentiment(symbol)
                
                recommendation_service = RecommendationService()
                recommendation_service.generate_recommendation(symbol)
                
                messages.info(request, f'Data refreshed for {symbol}')
            except Exception as e:
                messages.warning(request, f'Using cached data for {symbol} - refresh may be limited')
                
    except Stock.DoesNotExist:
        # Fetch stock data from API or create demo data
        stock_service = StockDataService()
        stock = stock_service.fetch_stock_info(symbol)
        
        if not stock:
            messages.error(request, f'Stock {symbol} not found. Please check the symbol and try again.')
            return redirect('dashboard')
        
        # Fetch additional data
        try:
            stock_service.fetch_historical_data(symbol)
            stock_service.calculate_technical_indicators(symbol)
            
            # Fetch news and calculate sentiment
            news_service = NewsService()
            news_service.fetch_stock_news(symbol)
            
            sentiment_service = SentimentAnalysisService()
            sentiment_service.calculate_daily_sentiment(symbol)
            
            # Generate recommendation
            recommendation_service = RecommendationService()
            recommendation_service.generate_recommendation(symbol)
            
            # Determine data source
            if stock_service.use_api or news_service.use_api:
                messages.success(request, f'Successfully loaded data for {symbol}')
            else:
                messages.info(request, f'Loaded demo data for {symbol} - add API keys for real-time data')
            
        except Exception as e:
            messages.warning(request, f'Some data may be limited: {str(e)}')
    #Developed By RAJ SHARMA
    # Get latest data
    latest_price = stock.prices.first()
    latest_technical = stock.technical_indicators.first()
    latest_sentiment = stock.sentiment_data.first()
    latest_recommendation = stock.recommendations.first()
    recent_news = stock.news_articles.all()[:5]
    price_history = stock.prices.all()[:30]
    
    # Get real-time quote if available
    stock_service = StockDataService()
    realtime_quote = stock_service.fetch_realtime_quote(symbol)
    
    # Check if user has this stock in any portfolio
    user_has_stock = False
    if request.user.is_authenticated:
        user_has_stock = PortfolioPosition.objects.filter(
            portfolio__user=request.user,
            stock=stock
        ).exists()
    
    context = {
        'stock': stock,
        'latest_price': latest_price,
        'latest_technical': latest_technical,
        'latest_sentiment': latest_sentiment,
        'latest_recommendation': latest_recommendation,
        'recent_news': recent_news,
        'price_history': price_history,
        'realtime_quote': realtime_quote,
        'user_has_stock': user_has_stock,
    }
    
    return render(request, 'spcm_app/stock_analysis.html', context)
#Developed By RAJ SHARMA
def stock_search(request):
    """Enhanced stock search with real-time data fetching"""
    if request.method == 'POST':
        form = StockSearchForm(request.POST)
        if form.is_valid():
            symbol = form.cleaned_data['symbol'].upper()
            
            # Check if stock exists locally
            try:
                stock = Stock.objects.get(symbol=symbol)
                return redirect('stock_analysis', symbol=symbol)
            except Stock.DoesNotExist:
                # Try to fetch from API
                stock_service = StockDataService()
                stock = stock_service.fetch_stock_info(symbol)
                
                if stock:
                    messages.success(request, f'Found {symbol}! Fetching real-time data...')
                    return redirect('stock_analysis', symbol=symbol)
                else:
                    messages.error(request, f'Stock {symbol} not found. Please check the symbol and try again.')
    
    return redirect('dashboard')
#Developed By RAJ SHARMA
# Authentication Views
class CustomLoginView(LoginView):
    """Custom login view"""
    form_class = CustomAuthenticationForm
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard')
    
    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().first_name or form.get_user().username}!')
        return super().form_valid(form)

class CustomLogoutView(LogoutView):
    """Custom logout view"""
    next_page = 'dashboard'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, 'You have been successfully logged out.')
        return super().dispatch(request, *args, **kwargs)

def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created successfully for {username}! You can now log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile_view(request):
    """User profile view"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
    
    # Get user statistics
    user_portfolios = Portfolio.objects.filter(user=request.user)
    total_portfolios = user_portfolios.count()
    total_positions = PortfolioPosition.objects.filter(portfolio__user=request.user).count()
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'total_portfolios': total_portfolios,
        'total_positions': total_positions,
    }
    
    return render(request, 'registration/profile.html', context)

@login_required
def change_password_view(request):
    """Change password view"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'registration/change_password.html', {'form': form})

@login_required
def portfolio_list(request):
    """List user portfolios"""
    portfolios = Portfolio.objects.filter(user=request.user, is_active=True)
    
    context = {
        'portfolios': portfolios,
    }
    
    return render(request, 'spcm_app/portfolio_list.html', context)

@login_required
def portfolio_detail(request, portfolio_id):
    """Portfolio detail view"""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    positions = portfolio.positions.select_related('stock').all()
    
    # Calculate portfolio metrics
    total_value = portfolio.total_value
    total_gain_loss = portfolio.total_gain_loss
    
    context = {
        'portfolio': portfolio,
        'positions': positions,
        'total_value': total_value,
        'total_gain_loss': total_gain_loss,
        'position_form': PositionForm(),
    }
    
    return render(request, 'spcm_app/portfolio_detail.html', context)

@login_required
def create_portfolio(request):
    """Create new portfolio"""
    if request.method == 'POST':
        form = PortfolioForm(request.POST)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.user = request.user
            portfolio.save()
            messages.success(request, 'Portfolio created successfully!')
            return redirect('portfolio_detail', portfolio_id=portfolio.id)
    else:
        form = PortfolioForm()
    
    return render(request, 'spcm_app/create_portfolio.html', {'form': form})

@login_required
def add_position(request, portfolio_id):
    """Add position to portfolio"""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    
    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            position = form.save(commit=False)
            position.portfolio = portfolio
            position.save()
            messages.success(request, 'Position added successfully!')
            return redirect('portfolio_detail', portfolio_id=portfolio.id)
        else:
            messages.error(request, 'Error adding position. Please check the form.')
    
    return redirect('portfolio_detail', portfolio_id=portfolio.id)

@login_required
def delete_portfolio(request, portfolio_id):
    """Delete portfolio"""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    
    if request.method == 'POST':
        portfolio.is_active = False
        portfolio.save()
        messages.success(request, f'Portfolio "{portfolio.name}" has been deleted.')
        return redirect('portfolio_list')
    
    return render(request, 'spcm_app/delete_portfolio.html', {'portfolio': portfolio})


def news_analysis(request, symbol):
    """News analysis for a specific stock"""
    stock = get_object_or_404(Stock, symbol=symbol.upper())

    # Get the latest 20 news articles
    news_articles = stock.news_articles.all().order_by('-published_at')[:20]

    # Since news_articles is sliced, convert to list and filter in Python
    positive = sum(1 for article in news_articles if article.sentiment_score > 0.1)
    negative = sum(1 for article in news_articles if article.sentiment_score < -0.1)
    neutral = len(news_articles) - positive - negative

    sentiment_stats = {
        'positive': positive,
        'neutral': neutral,
        'negative': negative,
    }

    context = {
        'stock': stock,
        'news_articles': news_articles,
        'sentiment_stats': sentiment_stats,
    }

    return render(request, 'spcm_app/news_analysis.html', context)


def refresh_stock_data(request, symbol):
    """API endpoint to refresh stock data"""
    if request.method == 'POST':
        try:
            symbol = symbol.upper()
            
            # Initialize services
            stock_service = StockDataService()
            news_service = NewsService()
            sentiment_service = SentimentAnalysisService()
            recommendation_service = RecommendationService()
            
            # Fetch fresh data
            stock = stock_service.fetch_stock_info(symbol)
            if not stock:
                return JsonResponse({'error': 'Stock not found'}, status=404)
            
            # Update data
            stock_service.fetch_historical_data(symbol)
            stock_service.calculate_technical_indicators(symbol)
            news_service.fetch_stock_news(symbol)
            sentiment_service.calculate_daily_sentiment(symbol)
            recommendation_service.generate_recommendation(symbol)
            
            return JsonResponse({
                'success': True,
                'message': f'Data refreshed for {symbol}',
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def api_stock_data(request, symbol):
    """API endpoint for stock data"""
    try:
        stock = Stock.objects.get(symbol=symbol.upper())
        latest_price = stock.prices.first()
        latest_sentiment = stock.sentiment_data.first()
        latest_recommendation = stock.recommendations.first()
        
        # Get real-time quote
        stock_service = StockDataService()
        realtime_quote = stock_service.fetch_realtime_quote(symbol.upper())
        
        data = {
            'symbol': stock.symbol,
            'name': stock.name,
            'price': float(latest_price.close_price) if latest_price else 0,
            'sentiment': float(latest_sentiment.overall_sentiment) if latest_sentiment else 0,
            'recommendation': latest_recommendation.recommendation if latest_recommendation else 'HOLD',
            'confidence': float(latest_recommendation.confidence_score) if latest_recommendation else 0,
            'realtime_quote': realtime_quote,
        }
        
        return JsonResponse(data)
    except Stock.DoesNotExist:
        return JsonResponse({'error': 'Stock not found'}, status=404)

def market_overview(request):
    """Market overview with sentiment analysis"""
    # Get top stocks by market cap
    top_stocks = Stock.objects.filter(is_active=True).order_by('-market_cap')[:20]
    
    # Get overall market sentiment
    today = timezone.now().date()
    market_sentiment = SentimentData.objects.filter(date=today).aggregate(
        avg_sentiment=models.Avg('overall_sentiment'),
        total_mentions=models.Sum('news_mentions')
    )
    
    # Get recent recommendations summary
    recommendations_summary = StockRecommendation.objects.filter(
        date=today
    ).values('recommendation').annotate(count=models.Count('recommendation'))
    
    context = {
        'top_stocks': top_stocks,
        'market_sentiment': market_sentiment.get('avg_sentiment', 0) or 0,
        'total_mentions': market_sentiment.get('total_mentions', 0) or 0,
        'recommendations_summary': recommendations_summary,
    }
    
    return render(request, 'spcm_app/market_overview.html', context)
