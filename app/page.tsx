"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { TrendingUp, TrendingDown, Minus, Search, BarChart3, MessageSquare, Target, Wallet } from "lucide-react"
import StockChart from "@/components/stock-chart"
import SentimentAnalysis from "@/components/sentiment-analysis"
import TechnicalIndicators from "@/components/technical-indicators"
import RecommendationEngine from "@/components/recommendation-engine"
import PortfolioTracker from "@/components/portfolio-tracker"
import NewsAnalysis from "@/components/news-analysis"

// Mock stock data
const mockStockData = {
  AAPL: {
    name: "Apple Inc.",
    price: 185.92,
    change: 2.34,
    changePercent: 1.28,
    sentiment: 0.65,
    recommendation: "BUY",
    confidence: 78,
    technicals: {
      rsi: 58.2,
      sma20: 182.45,
      sma50: 178.9,
      volume: 45678900,
    },
  },
  TSLA: {
    name: "Tesla Inc.",
    price: 248.5,
    change: -5.67,
    changePercent: -2.23,
    sentiment: 0.42,
    recommendation: "HOLD",
    confidence: 65,
    technicals: {
      rsi: 45.8,
      sma20: 252.3,
      sma50: 245.6,
      volume: 38945600,
    },
  },
  GOOGL: {
    name: "Alphabet Inc.",
    price: 142.18,
    change: 1.89,
    changePercent: 1.35,
    sentiment: 0.58,
    recommendation: "BUY",
    confidence: 72,
    technicals: {
      rsi: 62.1,
      sma20: 140.25,
      sma50: 138.75,
      volume: 28456700,
    },
  },
}

export default function SPCMDashboard() {
  const [selectedStock, setSelectedStock] = useState("AAPL")
  const [searchQuery, setSearchQuery] = useState("")
  const [stockData, setStockData] = useState(mockStockData[selectedStock])
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  useEffect(() => {
    setStockData(mockStockData[selectedStock])
  }, [selectedStock])

  const handleStockSearch = () => {
    const query = searchQuery.toUpperCase()
    if (mockStockData[query]) {
      setSelectedStock(query)
      setSearchQuery("")
    }
  }

  const analyzeStock = async () => {
    setIsAnalyzing(true)
    // Simulate analysis delay
    await new Promise((resolve) => setTimeout(resolve, 2000))
    setIsAnalyzing(false)
  }

  const getRecommendationColor = (rec: string) => {
    switch (rec) {
      case "BUY":
        return "bg-green-500"
      case "SELL":
        return "bg-red-500"
      case "HOLD":
        return "bg-yellow-500"
      default:
        return "bg-gray-500"
    }
  }

  const getRecommendationIcon = (rec: string) => {
    switch (rec) {
      case "BUY":
        return <TrendingUp className="h-4 w-4" />
      case "SELL":
        return <TrendingDown className="h-4 w-4" />
      case "HOLD":
        return <Minus className="h-4 w-4" />
      default:
        return <Minus className="h-4 w-4" />
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-gray-900">SPCM</h1>
          <p className="text-xl text-gray-600">Sentiment-Based Stock Recommendation System</p>
          <p className="text-sm text-gray-500">
            AI-Powered Stock Analysis with Real-time Sentiment & Technical Indicators
          </p>
        </div>

        {/* Stock Search */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Search className="h-5 w-5" />
              Stock Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-2 mb-4">
              <Input
                placeholder="Enter stock symbol (AAPL, TSLA, GOOGL)"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleStockSearch()}
              />
              <Button onClick={handleStockSearch}>Search</Button>
              <Button onClick={analyzeStock} disabled={isAnalyzing}>
                {isAnalyzing ? "Analyzing..." : "Analyze"}
              </Button>
            </div>

            {/* Quick Stock Buttons */}
            <div className="flex gap-2 flex-wrap">
              {Object.keys(mockStockData).map((symbol) => (
                <Button
                  key={symbol}
                  variant={selectedStock === symbol ? "default" : "outline"}
                  size="sm"
                  onClick={() => setSelectedStock(symbol)}
                >
                  {symbol}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Current Stock Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">{stockData.name}</CardTitle>
              <CardDescription>{selectedStock}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${stockData.price}</div>
              <div
                className={`flex items-center gap-1 text-sm ${stockData.change >= 0 ? "text-green-600" : "text-red-600"}`}
              >
                {stockData.change >= 0 ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
                {stockData.change >= 0 ? "+" : ""}
                {stockData.change} ({stockData.changePercent}%)
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">Sentiment Score</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{(stockData.sentiment * 100).toFixed(0)}%</div>
              <Progress value={stockData.sentiment * 100} className="mt-2" />
              <div className="text-sm text-gray-600 mt-1">
                {stockData.sentiment > 0.6 ? "Very Positive" : stockData.sentiment > 0.4 ? "Neutral" : "Negative"}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">Recommendation</CardTitle>
            </CardHeader>
            <CardContent>
              <Badge className={`${getRecommendationColor(stockData.recommendation)} text-white`}>
                <div className="flex items-center gap-1">
                  {getRecommendationIcon(stockData.recommendation)}
                  {stockData.recommendation}
                </div>
              </Badge>
              <div className="text-sm text-gray-600 mt-2">Confidence: {stockData.confidence}%</div>
              <Progress value={stockData.confidence} className="mt-1" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">Volume</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{(stockData.technicals.volume / 1000000).toFixed(1)}M</div>
              <div className="text-sm text-gray-600">Trading Volume</div>
            </CardContent>
          </Card>
        </div>

        {/* Analysis Progress */}
        {isAnalyzing && (
          <Alert>
            <BarChart3 className="h-4 w-4" />
            <AlertDescription>
              Analyzing sentiment from news sources and social media... This may take a few moments.
            </AlertDescription>
          </Alert>
        )}

        {/* Main Analysis Tabs */}
        <Tabs defaultValue="chart" className="space-y-4">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="chart" className="flex items-center gap-1">
              <BarChart3 className="h-4 w-4" />
              Chart
            </TabsTrigger>
            <TabsTrigger value="sentiment" className="flex items-center gap-1">
              <MessageSquare className="h-4 w-4" />
              Sentiment
            </TabsTrigger>
            <TabsTrigger value="technical" className="flex items-center gap-1">
              <TrendingUp className="h-4 w-4" />
              Technical
            </TabsTrigger>
            <TabsTrigger value="recommendation" className="flex items-center gap-1">
              <Target className="h-4 w-4" />
              AI Recommendation
            </TabsTrigger>
            <TabsTrigger value="news" className="flex items-center gap-1">
              <MessageSquare className="h-4 w-4" />
              News Analysis
            </TabsTrigger>
            <TabsTrigger value="portfolio" className="flex items-center gap-1">
              <Wallet className="h-4 w-4" />
              Portfolio
            </TabsTrigger>
          </TabsList>

          <TabsContent value="chart">
            <StockChart symbol={selectedStock} data={stockData} />
          </TabsContent>

          <TabsContent value="sentiment">
            <SentimentAnalysis symbol={selectedStock} sentimentScore={stockData.sentiment} />
          </TabsContent>

          <TabsContent value="technical">
            <TechnicalIndicators data={stockData.technicals} />
          </TabsContent>

          <TabsContent value="recommendation">
            <RecommendationEngine
              symbol={selectedStock}
              recommendation={stockData.recommendation}
              confidence={stockData.confidence}
              sentiment={stockData.sentiment}
              technicals={stockData.technicals}
            />
          </TabsContent>

          <TabsContent value="news">
            <NewsAnalysis symbol={selectedStock} />
          </TabsContent>

          <TabsContent value="portfolio">
            <PortfolioTracker />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
