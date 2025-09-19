"""
SPCM Business Logic Services - Enhanced with Fallback System
"""
import requests
from textblob import TextBlob
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
import logging
from decimal import Decimal
import json
import time
import random

from .models import (
    Stock, StockPrice, TechnicalIndicator, NewsArticle, 
    SentimentData, StockRecommendation
)

logger = logging.getLogger(__name__)

class StockDataService:
    """Service for fetching stock data with fallback to demo data"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'ALPHA_VANTAGE_API_KEY', None)
        self.base_url = 'https://www.alphavantage.co/query'
        self.use_api = bool(self.api_key and self.api_key != 'demo' and self.api_key.strip())
        
    def fetch_stock_info(self, symbol):
        """Fetch basic stock information with fallback to demo data"""
        try:
            # First try to get existing stock
            try:
                stock = Stock.objects.get(symbol=symbol)
                logger.info(f"Found existing stock {symbol}")
                return stock
            except Stock.DoesNotExist:
                pass
            
            # Try API if available
            if self.use_api:
                try:
                    return self._fetch_from_api(symbol)
                except Exception as e:
                    logger.warning(f"API fetch failed for {symbol}: {e}, falling back to demo data")
            
            # Fallback to demo data
            return self._create_demo_stock(symbol)
            
        except Exception as e:
            logger.error(f"Error fetching stock info for {symbol}: {e}")
            return None
    
    def _fetch_from_api(self, symbol):
        """Fetch from Alpha Vantage API"""
        params = {
            'function': 'OVERVIEW',
            'symbol': symbol,
            'apikey': self.api_key
        }
        
        response = requests.get(self.base_url, params=params, timeout=10)
        data = response.json()
        
        # Check for API errors
        if 'Error Message' in data:
            raise Exception(f"Alpha Vantage error: {data['Error Message']}")
            
        if 'Note' in data:
            raise Exception(f"Alpha Vantage rate limit: {data['Note']}")
        
        # Extract company information
        name = data.get('Name', f'{symbol} Corporation')
        sector = data.get('Sector', 'Technology')
        industry = data.get('Industry', 'Software')
        market_cap = self._parse_market_cap(data.get('MarketCapitalization', '0'))
        
        # Create stock
        stock = Stock.objects.create(
            symbol=symbol,
            name=name,
            sector=sector,
            industry=industry,
            market_cap=market_cap,
        )
        
        logger.info(f"Successfully fetched stock info from API for {symbol}")
        return stock
    
    def _create_demo_stock(self, symbol):
        """Create demo stock data"""
        demo_stocks = {
            'AAPL': {
                'name': 'Apple Inc.',
                'sector': 'Technology',
                'industry': 'Consumer Electronics',
                'market_cap': 3000000000000,
            },
            'TSLA': {
                'name': 'Tesla Inc.',
                'sector': 'Consumer Cyclical',
                'industry': 'Auto Manufacturers',
                'market_cap': 800000000000,
            },
            'GOOGL': {
                'name': 'Alphabet Inc.',
                'sector': 'Communication Services',
                'industry': 'Internet Content & Information',
                'market_cap': 1700000000000,
            },
            'MSFT': {
                'name': 'Microsoft Corporation',
                'sector': 'Technology',
                'industry': 'Software—Infrastructure',
                'market_cap': 2800000000000,
            },
            'AMZN': {
                'name': 'Amazon.com Inc.',
                'sector': 'Consumer Cyclical',
                'industry': 'Internet Retail',
                'market_cap': 1500000000000,
            }
        }
        
        stock_data = demo_stocks.get(symbol, {
            'name': f'{symbol} Corporation',
            'sector': 'Technology',
            'industry': 'Software',
            'market_cap': 1000000000000,
        })
        
        stock = Stock.objects.create(
            symbol=symbol,
            **stock_data
        )
        
        logger.info(f"Created demo stock data for {symbol}")
        return stock
    
    def fetch_historical_data(self, symbol, period='3month'):
        """Fetch historical stock price data with fallback"""
        try:
            stock = Stock.objects.get(symbol=symbol)
            
            # Try API if available
            if self.use_api:
                try:
                    return self._fetch_historical_from_api(stock, symbol)
                except Exception as e:
                    logger.warning(f"API historical data fetch failed for {symbol}: {e}, using demo data")
            
            # Fallback to demo data
            return self._generate_demo_historical_data(stock)
            
        except Stock.DoesNotExist:
            logger.error(f"Stock {symbol} not found in database")
            return False
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return False
    
    def _fetch_historical_from_api(self, stock, symbol):
        """Fetch historical data from Alpha Vantage"""
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': 'compact',
            'apikey': self.api_key
        }
        
        response = requests.get(self.base_url, params=params, timeout=15)
        data = response.json()
        
        if 'Error Message' in data:
            raise Exception(f"Alpha Vantage error: {data['Error Message']}")
            
        if 'Note' in data:
            raise Exception(f"Alpha Vantage rate limit: {data['Note']}")
        
        time_series = data.get('Time Series (Daily)', {})
        
        if not time_series:
            raise Exception("No time series data found")
        
        # Process and save price data
        for date_str, price_data in time_series.items():
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                StockPrice.objects.update_or_create(
                    stock=stock,
                    date=date,
                    defaults={
                        'open_price': Decimal(price_data['1. open']),
                        'high_price': Decimal(price_data['2. high']),
                        'low_price': Decimal(price_data['3. low']),
                        'close_price': Decimal(price_data['4. close']),
                        'volume': int(price_data['5. volume']),
                        'adjusted_close': Decimal(price_data['4. close']),
                    }
                )
            except (ValueError, KeyError) as e:
                logger.error(f"Error processing price data for {symbol} on {date_str}: {e}")
                continue
        
        logger.info(f"Successfully fetched historical data from API for {symbol}")
        return True
    
    def _generate_demo_historical_data(self, stock):
        """Generate demo historical price data"""
        base_prices = {
            'AAPL': 185.92,
            'TSLA': 248.50,
            'GOOGL': 142.18,
            'MSFT': 378.85,
            'AMZN': 155.89,
        }
        
        base_price = base_prices.get(stock.symbol, 100.0)
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
        
        logger.info(f"Generated demo historical data for {stock.symbol}")
        return True
    
    def fetch_realtime_quote(self, symbol):
        """Fetch real-time quote with fallback"""
        try:
            if self.use_api:
                try:
                    return self._fetch_quote_from_api(symbol)
                except Exception as e:
                    logger.warning(f"API quote fetch failed for {symbol}: {e}")
            
            # Fallback to latest price from database
            return self._get_latest_quote_from_db(symbol)
            
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return None
    
    def _fetch_quote_from_api(self, symbol):
        """Fetch quote from Alpha Vantage API"""
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': self.api_key
        }
        
        response = requests.get(self.base_url, params=params, timeout=10)
        data = response.json()
        
        if 'Error Message' in data:
            raise Exception(f"Alpha Vantage error: {data['Error Message']}")
            
        if 'Note' in data:
            raise Exception(f"Alpha Vantage rate limit: {data['Note']}")
        
        quote = data.get('Global Quote', {})
        
        if not quote:
            raise Exception("No quote data found")
        
        return {
            'symbol': quote.get('01. symbol'),
            'price': float(quote.get('05. price', 0)),
            'change': float(quote.get('09. change', 0)),
            'change_percent': quote.get('10. change percent', '0%').replace('%', ''),
            'volume': int(quote.get('06. volume', 0)),
            'latest_trading_day': quote.get('07. latest trading day'),
        }
    
    def _get_latest_quote_from_db(self, symbol):
        """Get latest quote from database"""
        try:
            stock = Stock.objects.get(symbol=symbol)
            latest_price = stock.prices.first()
            
            if latest_price:
                # Calculate mock change
                previous_price = stock.prices.all()[1] if stock.prices.count() > 1 else latest_price
                change = float(latest_price.close_price) - float(previous_price.close_price)
                change_percent = (change / float(previous_price.close_price)) * 100 if previous_price.close_price else 0
                
                return {
                    'symbol': symbol,
                    'price': float(latest_price.close_price),
                    'change': change,
                    'change_percent': f"{change_percent:.2f}%",
                    'volume': latest_price.volume,
                    'latest_trading_day': latest_price.date.isoformat(),
                }
            
            return None
            
        except Stock.DoesNotExist:
            return None
    
    def calculate_technical_indicators(self, symbol):
        """Calculate technical indicators"""
        try:
            stock = Stock.objects.get(symbol=symbol)
            self._calculate_local_indicators(stock)
            logger.info(f"Technical indicators calculated for {symbol}")
            return True
            
        except Stock.DoesNotExist:
            logger.error(f"Stock {symbol} not found")
            return False
        except Exception as e:
            logger.error(f"Error calculating technical indicators for {symbol}: {e}")
            return False
    
    def _calculate_local_indicators(self, stock):
        """Calculate technical indicators locally from price data"""
        prices = StockPrice.objects.filter(stock=stock).order_by('date')
        
        if prices.count() < 20:
            return
        
        # Convert to pandas for easier calculation
        df = pd.DataFrame(list(prices.values('date', 'close_price', 'volume')))
        df['close_price'] = df['close_price'].astype(float)
        
        # Calculate RSI
        df['rsi'] = self._calculate_rsi(df['close_price'])
        
        # Calculate SMAs
        df['sma_20'] = df['close_price'].rolling(window=20).mean()
        df['sma_50'] = df['close_price'].rolling(window=50).mean()
        
        # Calculate MACD
        ema_12 = df['close_price'].ewm(span=12).mean()
        ema_26 = df['close_price'].ewm(span=26).mean()
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        
        # Calculate Bollinger Bands
        df['bb_middle'] = df['sma_20']
        bb_std = df['close_price'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        
        # Save indicators to database
        for index, row in df.iterrows():
            if pd.notna(row['rsi']):
                TechnicalIndicator.objects.update_or_create(
                    stock=stock,
                    date=row['date'],
                    defaults={
                        'rsi': Decimal(str(round(row['rsi'], 2))) if pd.notna(row['rsi']) else None,
                        'sma_20': Decimal(str(round(row['sma_20'], 2))) if pd.notna(row['sma_20']) else None,
                        'sma_50': Decimal(str(round(row['sma_50'], 2))) if pd.notna(row['sma_50']) else None,
                        'macd': Decimal(str(round(row['macd'], 4))) if pd.notna(row['macd']) else None,
                        'macd_signal': Decimal(str(round(row['macd_signal'], 4))) if pd.notna(row['macd_signal']) else None,
                        'bollinger_upper': Decimal(str(round(row['bb_upper'], 2))) if pd.notna(row['bb_upper']) else None,
                        'bollinger_lower': Decimal(str(round(row['bb_lower'], 2))) if pd.notna(row['bb_lower']) else None,
                    }
                )
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _parse_market_cap(self, market_cap_str):
        """Parse market cap string to integer"""
        try:
            if not market_cap_str or market_cap_str == 'None':
                return 0
            return int(float(market_cap_str.replace(',', '')))
        except (ValueError, AttributeError):
            return 0

class NewsService:
    """Service for fetching news data with fallback"""
    
    def __init__(self):
        self.news_api_key = getattr(settings, 'NEWS_API_KEY', None)
        self.news_api_url = 'https://newsapi.org/v2/everything'
        self.use_api = bool(self.news_api_key and self.news_api_key != 'demo' and self.news_api_key.strip())
    
    def fetch_stock_news(self, symbol, days=7):
        """Fetch news articles with fallback to demo data"""
        try:
            stock = Stock.objects.get(symbol=symbol)
            
            # Try API if available
            if self.use_api:
                try:
                    return self._fetch_news_from_api(stock, symbol, days)
                except Exception as e:
                    logger.warning(f"API news fetch failed for {symbol}: {e}, using demo data")
            
            # Fallback to demo data
            return self._generate_demo_news(stock)
            
        except Stock.DoesNotExist:
            logger.error(f"Stock {symbol} not found")
            return False
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return False
    
    def _fetch_news_from_api(self, stock, symbol, days):
        """Fetch news from NewsAPI"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        params = {
            'q': f'{symbol} OR {stock.name}',
            'from': start_date.isoformat(),
            'to': end_date.isoformat(),
            'sortBy': 'publishedAt',
            'language': 'en',
            'apiKey': self.news_api_key
        }
        
        response = requests.get(self.news_api_url, params=params, timeout=15)
        data = response.json()
        
        if data.get('status') != 'ok':
            raise Exception(f"NewsAPI error: {data.get('message', 'Unknown error')}")
        
        articles = data.get('articles', [])
        
        for article_data in articles[:20]:
            try:
                published_at = datetime.fromisoformat(
                    article_data['publishedAt'].replace('Z', '+00:00')
                )
                
                content = f"{article_data.get('title', '')} {article_data.get('description', '')}"
                sentiment_score = self.analyze_sentiment(content)
                impact_score = self._determine_impact_score(article_data.get('source', {}).get('name', ''))
                
                NewsArticle.objects.update_or_create(
                    stock=stock,
                    url=article_data['url'],
                    defaults={
                        'title': article_data.get('title', '')[:500],
                        'content': article_data.get('content', '')[:5000],
                        'summary': article_data.get('description', '')[:1000],
                        'source': article_data.get('source', {}).get('name', 'Unknown')[:100],
                        'author': article_data.get('author', '')[:200],
                        'published_at': published_at,
                        'sentiment_score': Decimal(str(sentiment_score)),
                        'impact_score': impact_score,
                    }
                )
            except Exception as e:
                logger.error(f"Error processing article for {symbol}: {e}")
                continue
        
        logger.info(f"Fetched {len(articles)} news articles from API for {symbol}")
        return True
    
    def _generate_demo_news(self, stock):
        """Generate demo news articles"""
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
        
        articles = news_templates.get(stock.symbol, [
            (f"{stock.symbol} Shows Strong Performance", f"{stock.name} continues to demonstrate solid fundamentals.", 0.5),
            (f"Analysts Bullish on {stock.symbol}", f"Market analysts express optimism about {stock.name}'s prospects.", 0.6),
            (f"{stock.symbol} Faces Market Headwinds", f"{stock.name} navigating challenging market conditions.", -0.2),
        ])
        
        for i, (title, summary, sentiment) in enumerate(articles):
            published_date = timezone.now() - timedelta(days=random.randint(1, 7))
            
            NewsArticle.objects.update_or_create(
                stock=stock,
                title=title,
                defaults={
                    'content': summary + " " + "This is additional content for the news article providing more detailed analysis and context.",
                    'summary': summary,
                    'source': random.choice(['Reuters', 'Bloomberg', 'CNBC', 'Financial Times']),
                    'author': f'Reporter {i+1}',
                    'url': f'https://example.com/news/{stock.symbol.lower()}-{i+1}',
                    'published_at': published_date,
                    'sentiment_score': Decimal(str(sentiment)),
                    'impact_score': random.choice(['LOW', 'MEDIUM', 'HIGH']),
                }
            )
        
        logger.info(f"Generated demo news articles for {stock.symbol}")
        return True
    
    def analyze_sentiment(self, text):
        """Analyze sentiment using TextBlob"""
        try:
            blob = TextBlob(text)
            return round(blob.sentiment.polarity, 2)
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return 0.0
    
    def _determine_impact_score(self, source):
        """Determine impact score based on news source"""
        high_impact_sources = [
            'Reuters', 'Bloomberg', 'Wall Street Journal', 'Financial Times',
            'CNBC', 'MarketWatch', 'Yahoo Finance'
        ]
        
        medium_impact_sources = [
            'CNN', 'BBC', 'Associated Press', 'Forbes', 'Business Insider'
        ]
        
        if any(source_name in source for source_name in high_impact_sources):
            return 'HIGH'
        elif any(source_name in source for source_name in medium_impact_sources):
            return 'MEDIUM'
        else:
            return 'LOW'

class SentimentAnalysisService:
    """Service for aggregating and analyzing sentiment data"""
    
    def calculate_daily_sentiment(self, symbol, date=None):
        """Calculate daily sentiment aggregation for a stock"""
        try:
            if date is None:
                date = timezone.now().date()
            
            stock = Stock.objects.get(symbol=symbol)
            
            # Get news articles for the date range
            start_date = date - timedelta(days=3)
            news_articles = NewsArticle.objects.filter(
                stock=stock,
                published_at__date__gte=start_date,
                published_at__date__lte=date
            )
            
            if news_articles.exists():
                # Calculate weighted sentiment
                total_weight = 0
                weighted_sentiment = 0
                
                for article in news_articles:
                    weight = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}[article.impact_score]
                    weighted_sentiment += float(article.sentiment_score) * weight
                    total_weight += weight
                
                news_sentiment = weighted_sentiment / total_weight if total_weight > 0 else 0
                news_mentions = len(news_articles)
            else:
                news_sentiment = 0
                news_mentions = 0
            
            overall_sentiment = news_sentiment
            keywords = self._extract_keywords(news_articles)
            
            SentimentData.objects.update_or_create(
                stock=stock,
                date=date,
                defaults={
                    'news_sentiment': Decimal(str(round(news_sentiment, 2))),
                    'social_sentiment': Decimal(str(round(news_sentiment * 0.8, 2))),
                    'overall_sentiment': Decimal(str(round(overall_sentiment, 2))),
                    'news_mentions': news_mentions,
                    'social_mentions': news_mentions * 10,
                    'trending_keywords': keywords,
                }
            )
            
            logger.info(f"Calculated sentiment for {symbol} on {date}")
            return True
                
        except Stock.DoesNotExist:
            logger.error(f"Stock {symbol} not found")
            return False
        except Exception as e:
            logger.error(f"Error calculating sentiment for {symbol}: {e}")
            return False
    
    def _extract_keywords(self, articles):
        """Extract trending keywords from articles"""
        try:
            text = ' '.join([article.title + ' ' + article.summary for article in articles])
            
            keywords = []
            common_words = [
                'earnings', 'revenue', 'profit', 'growth', 'market', 'stock',
                'investment', 'analyst', 'upgrade', 'downgrade', 'buy', 'sell',
                'target', 'price', 'forecast', 'outlook', 'performance'
            ]
            
            text_lower = text.lower()
            for word in common_words:
                if word in text_lower:
                    keywords.append(word)
            
            return keywords[:5]
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []

class RecommendationService:
    """Service for generating AI-powered stock recommendations"""
    
    def generate_recommendation(self, symbol, date=None):
        """Generate comprehensive stock recommendation"""
        try:
            if date is None:
                date = timezone.now().date()
            
            stock = Stock.objects.get(symbol=symbol)
            
            # Get latest data
            latest_sentiment = stock.sentiment_data.first()
            latest_technical = stock.technical_indicators.first()
            latest_price = stock.prices.first()
            
            # Use default values if no data available
            sentiment_score = float(latest_sentiment.overall_sentiment) if latest_sentiment else 0.0
            
            # Technical analysis score
            technical_score = 0
            if latest_technical:
                rsi = float(latest_technical.rsi) if latest_technical.rsi else 50
                
                if rsi < 30:
                    technical_score += 0.3
                elif rsi > 70:
                    technical_score -= 0.3
                
                if latest_technical.sma_20 and latest_technical.sma_50:
                    if float(latest_technical.sma_20) > float(latest_technical.sma_50):
                        technical_score += 0.2
                    else:
                        technical_score -= 0.2
            
            # Combine scores
            combined_score = (sentiment_score * 0.6) + (technical_score * 0.4)
            
            # Generate recommendation
            if combined_score > 0.2:
                recommendation = 'BUY'
                confidence = min(90, 60 + abs(combined_score) * 100)
                risk_level = 'LOW' if combined_score > 0.4 else 'MEDIUM'
            elif combined_score < -0.2:
                recommendation = 'SELL'
                confidence = min(90, 60 + abs(combined_score) * 100)
                risk_level = 'HIGH'
            else:
                recommendation = 'HOLD'
                confidence = 50 + abs(combined_score) * 50
                risk_level = 'MEDIUM'
            
            # Calculate target price
            current_price = float(latest_price.close_price) if latest_price else 100
            
            if recommendation == 'BUY':
                target_price = current_price * (1 + max(0.05, combined_score))
            elif recommendation == 'SELL':
                target_price = current_price * (1 + min(-0.05, combined_score))
            else:
                target_price = current_price
            
            StockRecommendation.objects.update_or_create(
                stock=stock,
                date=date,
                defaults={
                    'recommendation': recommendation,
                    'confidence_score': Decimal(str(round(confidence, 2))),
                    'sentiment_weight': Decimal(str(round(sentiment_score * 100, 2))),
                    'technical_weight': Decimal(str(round(technical_score * 100, 2))),
                    'fundamental_weight': Decimal(str(round(50, 2))),
                    'risk_level': risk_level,
                    'target_price': Decimal(str(round(target_price, 2))),
                    'model_version': '2.0-enhanced'
                }
            )
            
            logger.info(f"Generated recommendation for {symbol}: {recommendation} ({confidence}%)")
            return True
            
        except Stock.DoesNotExist:
            logger.error(f"Stock {symbol} not found")
            return False
        except Exception as e:
            logger.error(f"Error generating recommendation for {symbol}: {e}")
            return False
