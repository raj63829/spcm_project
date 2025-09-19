"""
SPCM Sentiment Analysis Module
This script demonstrates the core sentiment analysis functionality
that would be used in the backend of the SPCM system.
"""
#Developed By RAJ SHARMA
import re
import json
from typing import List, Dict, Tuple
from datetime import datetime

class SentimentAnalyzer:
    def __init__(self):
        # Simple sentiment lexicon (in production, use VADER, TextBlob, or trained models)
        self.positive_words = {
            'excellent', 'great', 'good', 'positive', 'bullish', 'strong', 'growth',
