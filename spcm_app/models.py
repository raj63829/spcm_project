"""
SPCM Django Models
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import json

class Stock(models.Model):
    """Stock information model"""
    symbol = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    sector = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    market_cap = models.BigIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['symbol']

    def __str__(self):
        return f"{self.symbol} - {self.name}"

class StockPrice(models.Model):
    """Historical stock price data"""
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='prices')
    date = models.DateField(db_index=True)
    open_price = models.DecimalField(max_digits=10, decimal_places=2)
    high_price = models.DecimalField(max_digits=10, decimal_places=2)
    low_price = models.DecimalField(max_digits=10, decimal_places=2)
    close_price = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.BigIntegerField()
    adjusted_close = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ['stock', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.stock.symbol} - {self.date}"

class TechnicalIndicator(models.Model):
    """Technical indicators for stocks"""
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='technical_indicators')
    date = models.DateField(db_index=True)
    rsi = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    sma_20 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sma_50 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sma_200 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ema_12 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ema_26 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    macd = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    macd_signal = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    bollinger_upper = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bollinger_lower = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ['stock', 'date']
        ordering = ['-date']

class NewsArticle(models.Model):
    """News articles related to stocks"""
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='news_articles')
    title = models.CharField(max_length=500)
    content = models.TextField()
    summary = models.TextField(blank=True)
    source = models.CharField(max_length=100)
    author = models.CharField(max_length=200, blank=True)
    url = models.URLField()
    published_at = models.DateTimeField()
    sentiment_score = models.DecimalField(
        max_digits=3, decimal_places=2, 
        validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)],
        null=True, blank=True
    )
    impact_score = models.CharField(
        max_length=10, 
        choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High')],
        default='MEDIUM'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_at']
        unique_together = ['url', 'stock']

    def __str__(self):
        return f"{self.stock.symbol} - {self.title[:50]}"

class SentimentData(models.Model):
    """Aggregated sentiment data for stocks"""
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='sentiment_data')
    date = models.DateField(db_index=True)
    
    # Sentiment scores from different sources
    news_sentiment = models.DecimalField(
        max_digits=3, decimal_places=2,
        validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)],
        null=True, blank=True
    )
    social_sentiment = models.DecimalField(
        max_digits=3, decimal_places=2,
        validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)],
        null=True, blank=True
    )
    overall_sentiment = models.DecimalField(
        max_digits=3, decimal_places=2,
        validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)]
    )
    
    # Mention counts
    news_mentions = models.IntegerField(default=0)
    social_mentions = models.IntegerField(default=0)
    
    # Keywords (stored as JSON)
    trending_keywords = models.JSONField(default=list)

    class Meta:
        unique_together = ['stock', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.stock.symbol} - {self.date} - {self.overall_sentiment}"

class StockRecommendation(models.Model):
    """AI-generated stock recommendations"""
    RECOMMENDATION_CHOICES = [
        ('BUY', 'Buy'),
        ('HOLD', 'Hold'),
        ('SELL', 'Sell'),
    ]
    
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='recommendations')
    date = models.DateField(db_index=True)
    recommendation = models.CharField(max_length=4, choices=RECOMMENDATION_CHOICES)
    confidence_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    
    # Factors contributing to recommendation
    sentiment_weight = models.DecimalField(max_digits=5, decimal_places=2)
    technical_weight = models.DecimalField(max_digits=5, decimal_places=2)
    fundamental_weight = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Risk assessment
    risk_level = models.CharField(
        max_length=10,
        choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High')],
        default='MEDIUM'
    )
    
    # Target price
    target_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Model metadata
    model_version = models.CharField(max_length=50, default='1.0')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['stock', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.stock.symbol} - {self.recommendation} ({self.confidence_score}%)"

class Portfolio(models.Model):
    """User portfolio model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    @property
    def total_value(self):
        """Calculate total portfolio value"""
        return sum(position.current_value for position in self.positions.all())

    @property
    def total_gain_loss(self):
        """Calculate total gain/loss"""
        return sum(position.gain_loss for position in self.positions.all())

class PortfolioPosition(models.Model):
    """Individual stock positions in a portfolio"""
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='positions')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    shares = models.DecimalField(max_digits=10, decimal_places=4)
    average_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['portfolio', 'stock']

    def __str__(self):
        return f"{self.portfolio.name} - {self.stock.symbol} ({self.shares} shares)"

    @property
    def current_price(self):
        """Get current stock price"""
        latest_price = self.stock.prices.first()
        return latest_price.close_price if latest_price else self.average_price

    @property
    def current_value(self):
        """Calculate current position value"""
        return self.shares * self.current_price

    @property
    def cost_basis(self):
        """Calculate cost basis"""
        return self.shares * self.average_price

    @property
    def gain_loss(self):
        """Calculate gain/loss"""
        return self.current_value - self.cost_basis

    @property
    def gain_loss_percent(self):
        """Calculate gain/loss percentage"""
        if self.cost_basis == 0:
            return 0
        return (self.gain_loss / self.cost_basis) * 100

class UserProfile(models.Model):
    """Extended user profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    risk_tolerance = models.CharField(
        max_length=20,
        choices=[
            ('CONSERVATIVE', 'Conservative'),
            ('MODERATE', 'Moderate'),
            ('AGGRESSIVE', 'Aggressive')
        ],
        default='MODERATE'
    )
    investment_experience = models.CharField(
        max_length=20,
        choices=[
            ('BEGINNER', 'Beginner'),
            ('INTERMEDIATE', 'Intermediate'),
            ('ADVANCED', 'Advanced')
        ],
        default='BEGINNER'
    )
    preferred_sectors = models.JSONField(default=list)
    notification_preferences = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Profile"
