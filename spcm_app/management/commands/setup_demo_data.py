"""
Django management command to set up demo data without external APIs
Usage: python manage.py setup_demo_data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random
from decimal import Decimal

from spcm_app.models import (
    Stock, StockPrice, TechnicalIndicator, NewsArticle, 
    SentimentData, StockRecommendation
)

class Command(BaseCommand):
    help = 'Set up demo data for SPCM without requiring external APIs'

    def handle(self, *args, **options):
        self.stdout.write("Setting up demo data...")
        
        # Demo stocks data
        demo_stocks = [
            {
                'symbol': 'AAPL',
                'name': 'Apple Inc.',
                'sector': 'Technology',
                'industry': 'Consumer Electronics',
                'market_cap': 3000000000000,
                'base_price': 185.92
            },
            {
                'symbol': 'TSLA',
                'name': 'Tesla Inc.',
                'sector': 'Consumer Cyclical',
                'industry': 'Auto Manufacturers',
                'market_cap': 800000000000,
                'base_price': 248.50
            },
            {
                'symbol': 'GOOGL',
                'name': 'Alphabet Inc.',
                'sector': 'Communication Services',
                'industry': 'Internet Content & Information',
                'market_cap': 1700000000000,
                'base_price': 142.18
            },
            {
                'symbol': 'MSFT',
                'name': 'Microsoft Corporation',
                'sector': 'Technology',
                'industry': 'Software—Infrastructure',
                'market_cap': 2800000000000,
                'base_price': 378.85
            },
            {
                'symbol': 'AMZN',
                'name': 'Amazon.com Inc.',
                'sector': 'Consumer Cyclical',
                'industry': 'Internet Retail',
                'market_cap': 1500000000000,
                'base_price': 155.89
            }
        ]
        
        for stock_data in demo_stocks:
            self.create_stock_data(stock_data)
        
        self.stdout.write(
            self.style.SUCCESS('✅ Demo data setup completed successfully!')
        )
    
    def create_stock_data(self, stock_data):
        symbol = stock_data['symbol']
        self.stdout.write(f"Creating data for {symbol}...")
        
        # Create or update stock
        stock, created = Stock.objects.get_or_create(
            symbol=symbol,
            defaults={
                'name': stock_data['name'],
                'sector': stock_data['sector'],
                'industry': stock_data['industry'],
                'market_cap': stock_data['market_cap'],
            }
        )
        
        if not created:
            stock.name = stock_data['name']
            stock.sector = stock_data['sector']
            stock.industry = stock_data['industry']
            stock.market_cap = stock_data['market_cap']
            stock.save()
        
        # Generate historical price data (30 days)
        base_price = stock_data['base_price']
        current_date = timezone.now().date()
        
        for i in range(30, 0, -1):
            date = current_date - timedelta(days=i)
            
            # Generate realistic price movement
            daily_change = random.uniform(-0.05, 0.05)  # ±5% daily change
            if i == 1:  # Today's price
                price = base_price
            else:
                price = base_price * (1 + daily_change * (30 - i) / 30)
            
            # Generate OHLC data
            open_price = price * random.uniform(0.98, 1.02)
            high_price = max(open_price, price) * random.uniform(1.0, 1.03)
            low_price = min(open_price, price) * random.uniform(0.97, 1.0)
            close_price = price
            volume = random.randint(20000000, 100000000)
            
            StockPrice.objects.update_or_create(
                stock=stock,
                date=date,
                defaults={
                    'open_price': Decimal(str(round(open_price, 2))),
                    'high_price': Decimal(str(round(high_price, 2))),
                    'low_price': Decimal(str(round(low_price, 2))),
                    'close_price': Decimal(str(round(close_price, 2))),
                    'volume': volume,
                    'adjusted_close': Decimal(str(round(close_price, 2))),
                }
            )
        
        # Generate technical indicators
        self.generate_technical_indicators(stock)
        
        # Generate news articles
        self.generate_news_articles(stock)
        
        # Generate sentiment data
        self.generate_sentiment_data(stock)
        
        # Generate recommendations
        self.generate_recommendations(stock)
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ Created data for {symbol}')
        )
    
    def generate_technical_indicators(self, stock):
        """Generate mock technical indicators"""
        prices = StockPrice.objects.filter(stock=stock).order_by('date')
        
        for i, price in enumerate(prices):
            if i >= 20:  # Need at least 20 days for indicators
                # Mock RSI (14-day)
                rsi = random.uniform(30, 70)
                
                # Mock SMAs
                recent_prices = list(prices[max(0, i-19):i+1].values_list('close_price', flat=True))
                sma_20 = sum(recent_prices) / len(recent_prices) if recent_prices else price.close_price
                
                if i >= 50:
                    recent_50 = list(prices[max(0, i-49):i+1].values_list('close_price', flat=True))
                    sma_50 = sum(recent_50) / len(recent_50) if recent_50 else price.close_price
                else:
                    sma_50 = sma_20
                
                # Mock MACD
                macd = random.uniform(-2, 2)
                macd_signal = macd * random.uniform(0.8, 1.2)
                
                # Mock Bollinger Bands
                std_dev = float(sma_20) * 0.02  # 2% standard deviation
                bollinger_upper = float(sma_20) + (2 * std_dev)
                bollinger_lower = float(sma_20) - (2 * std_dev)
                
                TechnicalIndicator.objects.update_or_create(
                    stock=stock,
                    date=price.date,
                    defaults={
                        'rsi': Decimal(str(round(rsi, 2))),
                        'sma_20': Decimal(str(round(float(sma_20), 2))),
                        'sma_50': Decimal(str(round(float(sma_50), 2))),
                        'sma_200': Decimal(str(round(float(sma_50), 2))),  # Simplified
                        'ema_12': Decimal(str(round(float(sma_20), 2))),
                        'ema_26': Decimal(str(round(float(sma_50), 2))),
                        'macd': Decimal(str(round(macd, 4))),
                        'macd_signal': Decimal(str(round(macd_signal, 4))),
                        'bollinger_upper': Decimal(str(round(bollinger_upper, 2))),
                        'bollinger_lower': Decimal(str(round(bollinger_lower, 2))),
                    }
                )
    
    def generate_news_articles(self, stock):
        """Generate mock news articles"""
        news_templates = {
            'AAPL': [
                ("Apple Reports Strong Q4 Earnings", "Apple Inc. reported quarterly revenue of $89.5 billion, surpassing analyst expectations.", 0.75),
                ("New iPhone AI Features Drive Interest", "Apple's latest AI-powered features are generating significant consumer interest.", 0.65),
                ("Supply Chain Concerns May Impact Production", "Industry analysts warn about potential supply chain disruptions.", -0.35),
            ],
            'TSLA': [
                ("Tesla Delivery Numbers Fall Short", "Tesla reported delivery numbers below analyst estimates.", -0.45),
                ("Autopilot Technology Receives Update", "Tesla's latest Autopilot update includes enhanced safety features.", 0.70),
                ("EV Competition Intensifies", "Traditional automakers are expanding their EV offerings.", -0.25),
            ],
            'GOOGL': [
                ("Google Cloud Revenue Surges", "Alphabet's cloud division reported strong growth in latest quarter.", 0.80),
                ("Bard AI Chatbot Gains Capabilities", "Google's AI assistant receives significant updates.", 0.60),
                ("Regulatory Scrutiny Increases", "European regulators considering additional measures.", -0.40),
            ],
            'MSFT': [
                ("Microsoft Azure Growth Continues", "Azure cloud services show strong quarterly performance.", 0.75),
                ("AI Integration Across Products", "Microsoft integrating AI capabilities across product suite.", 0.65),
                ("Enterprise Adoption Increases", "More enterprises adopting Microsoft cloud solutions.", 0.55),
            ],
            'AMZN': [
                ("Amazon Prime Day Success", "Record-breaking sales during Prime Day event.", 0.70),
                ("AWS Market Share Grows", "Amazon Web Services maintains cloud market leadership.", 0.60),
                ("Logistics Challenges Persist", "Supply chain issues continue to impact operations.", -0.30),
            ]
        }
        
        articles = news_templates.get(stock.symbol, news_templates['AAPL'])
        
        for i, (title, summary, sentiment) in enumerate(articles):
            published_date = timezone.now() - timedelta(days=random.randint(1, 7))
            
            NewsArticle.objects.update_or_create(
                stock=stock,
                title=title,
                defaults={
                    'content': summary + " " + "This is additional content for the news article.",
                    'summary': summary,
                    'source': random.choice(['Reuters', 'Bloomberg', 'CNBC', 'Financial Times']),
                    'author': f'Reporter {i+1}',
                    'url': f'https://example.com/news/{stock.symbol.lower()}-{i+1}',
                    'published_at': published_date,
                    'sentiment_score': Decimal(str(sentiment)),
                    'impact_score': random.choice(['LOW', 'MEDIUM', 'HIGH']),
                }
            )
    
    def generate_sentiment_data(self, stock):
        """Generate mock sentiment data"""
        current_date = timezone.now().date()
        
        for i in range(7):  # Last 7 days
            date = current_date - timedelta(days=i)
            
            # Calculate sentiment based on news
            news_articles = NewsArticle.objects.filter(
                stock=stock,
                published_at__date=date
            )
            
            if news_articles.exists():
                news_sentiment = sum(float(article.sentiment_score) for article in news_articles) / len(news_articles)
                news_mentions = len(news_articles)
            else:
                news_sentiment = random.uniform(-0.2, 0.6)
                news_mentions = 0
            
            overall_sentiment = news_sentiment
            social_mentions = random.randint(50, 500)
            
            keywords = ['earnings', 'growth', 'innovation', 'market', 'technology']
            
            SentimentData.objects.update_or_create(
                stock=stock,
                date=date,
                defaults={
                    'news_sentiment': Decimal(str(round(news_sentiment, 2))),
                    'social_sentiment': Decimal(str(round(random.uniform(-0.1, 0.4), 2))),
                    'overall_sentiment': Decimal(str(round(overall_sentiment, 2))),
                    'news_mentions': news_mentions,
                    'social_mentions': social_mentions,
                    'trending_keywords': random.sample(keywords, 3),
                }
            )
    
    def generate_recommendations(self, stock):
        """Generate mock AI recommendations"""
        current_date = timezone.now().date()
        
        # Get latest data
        latest_sentiment = SentimentData.objects.filter(stock=stock).first()
        latest_technical = TechnicalIndicator.objects.filter(stock=stock).first()
        
        if latest_sentiment and latest_technical:
            sentiment_score = float(latest_sentiment.overall_sentiment)
            rsi = float(latest_technical.rsi)
            
            # Simple recommendation logic
            if sentiment_score > 0.3 and rsi < 70:
                recommendation = 'BUY'
                confidence = random.uniform(70, 90)
                risk_level = 'LOW'
            elif sentiment_score < -0.2 or rsi > 80:
                recommendation = 'SELL'
                confidence = random.uniform(60, 80)
                risk_level = 'HIGH'
            else:
                recommendation = 'HOLD'
                confidence = random.uniform(50, 70)
                risk_level = 'MEDIUM'
            
            latest_price = StockPrice.objects.filter(stock=stock).first()
            current_price = float(latest_price.close_price) if latest_price else 100
            
            if recommendation == 'BUY':
                target_price = current_price * 1.1
            elif recommendation == 'SELL':
                target_price = current_price * 0.9
            else:
                target_price = current_price
            
            StockRecommendation.objects.update_or_create(
                stock=stock,
                date=current_date,
                defaults={
                    'recommendation': recommendation,
                    'confidence_score': Decimal(str(round(confidence, 2))),
                    'sentiment_weight': Decimal(str(round(sentiment_score * 100, 2))),
                    'technical_weight': Decimal(str(round((100 - rsi), 2))),
                    'fundamental_weight': Decimal(str(round(random.uniform(40, 80), 2))),
                    'risk_level': risk_level,
                    'target_price': Decimal(str(round(target_price, 2))),
                    'model_version': '1.0-demo'
                }
            )
