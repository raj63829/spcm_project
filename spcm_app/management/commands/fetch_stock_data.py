"""
Django management command to fetch stock data with enhanced error handling
Usage: python manage.py fetch_stock_data AAPL TSLA GOOGL
"""
from django.core.management.base import BaseCommand
from spcm_app.services import StockDataService, NewsService, SentimentAnalysisService, RecommendationService
from spcm_app.models import Stock
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fetch stock data, news, and generate recommendations with fallback to demo data'

    def add_arguments(self, parser):
        parser.add_argument('symbols', nargs='+', type=str, help='Stock symbols to fetch')
        parser.add_argument('--days', type=int, default=30, help='Number of days of historical data')
        parser.add_argument('--news-days', type=int, default=7, help='Number of days of news data')
        parser.add_argument('--force-demo', action='store_true', help='Force use of demo data even if API keys are available')

    def handle(self, *args, **options):
        symbols = options['symbols']
        days = options['days']
        news_days = options['news_days']
        force_demo = options['force_demo']
        
        if force_demo:
            self.stdout.write(
                self.style.WARNING('🔧 Force demo mode enabled - using demo data regardless of API keys')
            )
        
        stock_service = StockDataService()
        news_service = NewsService()
        sentiment_service = SentimentAnalysisService()
        recommendation_service = RecommendationService()
        
        # Check API availability
        api_status = self._check_api_status(stock_service, news_service)
        
        for symbol in symbols:
            symbol = symbol.upper()
            self.stdout.write(f"🔄 Processing {symbol}...")
            
            try:
                # Temporarily disable API if force demo
                if force_demo:
                    stock_service.use_api = False
                    news_service.use_api = False
                
                # Fetch basic stock info
                stock = stock_service.fetch_stock_info(symbol)
                if not stock:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Failed to fetch stock info for {symbol}')
                    )
                    continue
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Stock info: {stock.name}')
                )
                
                # Fetch historical price data
                if stock_service.fetch_historical_data(symbol, period=f'{days}d'):
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Historical data for {symbol}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Historical data limited for {symbol}')
                    )
                
                # Calculate technical indicators
                if stock_service.calculate_technical_indicators(symbol):
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Technical indicators for {symbol}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Technical indicators limited for {symbol}')
                    )
                
                # Fetch news data
                if news_service.fetch_stock_news(symbol, days=news_days):
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ News data for {symbol}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  News data limited for {symbol}')
                    )
                
                # Calculate sentiment
                if sentiment_service.calculate_daily_sentiment(symbol):
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Sentiment analysis for {symbol}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Sentiment analysis limited for {symbol}')
                    )
                
                # Generate recommendation
                if recommendation_service.generate_recommendation(symbol):
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ AI recommendation for {symbol}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Recommendation limited for {symbol}')
                    )
                
                self.stdout.write(
                    self.style.SUCCESS(f'🎉 Completed processing {symbol}')
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'💥 Error processing {symbol}: {str(e)}')
                )
                logger.error(f"Error processing {symbol}: {e}")
        
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(f'🏁 Finished processing {len(symbols)} stocks')
        )
        
        # Show final status
        self._show_final_status(api_status)
    
    def _check_api_status(self, stock_service, news_service):
        """Check API availability status"""
        status = {
            'stock_api': stock_service.use_api,
            'news_api': news_service.use_api,
        }
        
        self.stdout.write('')
        self.stdout.write('📊 API Status:')
        
        if status['stock_api']:
            self.stdout.write(
                self.style.SUCCESS('✅ Alpha Vantage API: Available')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️  Alpha Vantage API: Using demo data (no API key or demo mode)')
            )
        
        if status['news_api']:
            self.stdout.write(
                self.style.SUCCESS('✅ NewsAPI: Available')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️  NewsAPI: Using demo data (no API key or demo mode)')
            )
        
        self.stdout.write('')
        return status
    
    def _show_final_status(self, api_status):
        """Show final status and recommendations"""
        self.stdout.write('')
        self.stdout.write('📋 Summary:')
        
        if not api_status['stock_api'] and not api_status['news_api']:
            self.stdout.write(
                self.style.WARNING('⚠️  Running in full demo mode')
            )
            self.stdout.write('💡 To enable real-time data:')
            self.stdout.write('   1. Get free Alpha Vantage API key: https://www.alphavantage.co/support/#api-key')
            self.stdout.write('   2. Get free NewsAPI key: https://newsapi.org/register')
            self.stdout.write('   3. Add keys to your .env file')
        elif not api_status['stock_api']:
            self.stdout.write(
                self.style.WARNING('⚠️  Stock data using demo mode')
            )
            self.stdout.write('💡 Add ALPHA_VANTAGE_API_KEY to .env for real stock data')
        elif not api_status['news_api']:
            self.stdout.write(
                self.style.WARNING('⚠️  News data using demo mode')
            )
            self.stdout.write('💡 Add NEWS_API_KEY to .env for real news data')
        else:
            self.stdout.write(
                self.style.SUCCESS('🚀 All APIs active - real-time data enabled!')
            )
        
        self.stdout.write('')
        self.stdout.write('🎯 Next steps:')
        self.stdout.write('   • Visit the dashboard to see your data')
        self.stdout.write('   • Search for stocks to get AI recommendations')
        self.stdout.write('   • Create portfolios to track your investments')
