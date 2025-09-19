"""
Django Admin Configuration for SPCM
"""
from django.contrib import admin
from .models import (
    Stock, StockPrice, TechnicalIndicator, NewsArticle, 
    SentimentData, StockRecommendation, Portfolio, 
    PortfolioPosition, UserProfile
)

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'name', 'sector', 'industry', 'is_active', 'created_at']
    list_filter = ['sector', 'industry', 'is_active']
    search_fields = ['symbol', 'name']
    ordering = ['symbol']

@admin.register(StockPrice)
class StockPriceAdmin(admin.ModelAdmin):
    list_display = ['stock', 'date', 'close_price', 'volume']
    list_filter = ['date', 'stock__symbol']
    search_fields = ['stock__symbol']
    ordering = ['-date']

@admin.register(TechnicalIndicator)
class TechnicalIndicatorAdmin(admin.ModelAdmin):
    list_display = ['stock', 'date', 'rsi', 'sma_20', 'sma_50']
    list_filter = ['date']
    search_fields = ['stock__symbol']
    ordering = ['-date']

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ['stock', 'title', 'source', 'sentiment_score', 'impact_score', 'published_at']
    list_filter = ['source', 'impact_score', 'published_at']
    search_fields = ['title', 'stock__symbol']
    ordering = ['-published_at']

@admin.register(SentimentData)
class SentimentDataAdmin(admin.ModelAdmin):
    list_display = ['stock', 'date', 'overall_sentiment', 'news_mentions', 'social_mentions']
    list_filter = ['date']
    search_fields = ['stock__symbol']
    ordering = ['-date']

@admin.register(StockRecommendation)
class StockRecommendationAdmin(admin.ModelAdmin):
    list_display = ['stock', 'date', 'recommendation', 'confidence_score', 'risk_level']
    list_filter = ['recommendation', 'risk_level', 'date']
    search_fields = ['stock__symbol']
    ordering = ['-date']

class PortfolioPositionInline(admin.TabularInline):
    model = PortfolioPosition
    extra = 0

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'name']
    inlines = [PortfolioPositionInline]

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'risk_tolerance', 'investment_experience']
    list_filter = ['risk_tolerance', 'investment_experience']
    search_fields = ['user__username']
