"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { TrendingUp, TrendingDown, Minus, Brain, Target, AlertTriangle } from "lucide-react"

interface RecommendationEngineProps {
  symbol: string
  recommendation: string
  confidence: number
  sentiment: number
  technicals: any
}

export default function RecommendationEngine({
  symbol,
  recommendation,
  confidence,
  sentiment,
  technicals,
}: RecommendationEngineProps) {
  const getRecommendationDetails = (rec: string) => {
    switch (rec) {
      case "BUY":
        return {
          color: "bg-green-500",
          textColor: "text-green-600",
          icon: TrendingUp,
          description: "Strong positive signals indicate potential upward movement",
          action: "Consider adding to position or initiating new position",
        }
      case "SELL":
        return {
          color: "bg-red-500",
          textColor: "text-red-600",
          icon: TrendingDown,
          description: "Negative indicators suggest potential downward pressure",
          action: "Consider reducing position or taking profits",
        }
      case "HOLD":
        return {
          color: "bg-yellow-500",
          textColor: "text-yellow-600",
          icon: Minus,
          description: "Mixed signals suggest maintaining current position",
          action: "Monitor closely for clearer directional signals",
        }
      default:
        return {
          color: "bg-gray-500",
          textColor: "text-gray-600",
          icon: Minus,
          description: "Insufficient data for clear recommendation",
          action: "Gather more information before making decisions",
        }
    }
  }

  const details = getRecommendationDetails(recommendation)
  const IconComponent = details.icon

  // Calculate individual factor scores
  const factors = {
    sentiment: {
      name: "Sentiment Analysis",
      score: sentiment * 100,
      weight: 30,
      signal: sentiment > 0.6 ? "Positive" : sentiment > 0.4 ? "Neutral" : "Negative",
    },
    technical: {
      name: "Technical Indicators",
      score: technicals.rsi < 30 ? 80 : technicals.rsi > 70 ? 20 : 60,
      weight: 40,
      signal: technicals.rsi < 30 ? "Oversold" : technicals.rsi > 70 ? "Overbought" : "Neutral",
    },
    momentum: {
      name: "Price Momentum",
      score: technicals.sma20 > technicals.sma50 ? 75 : 25,
      weight: 20,
      signal: technicals.sma20 > technicals.sma50 ? "Bullish" : "Bearish",
    },
    volume: {
      name: "Volume Analysis",
      score: 70, // Mock score
      weight: 10,
      signal: "Above Average",
    },
  }

  const riskLevel = confidence > 75 ? "Low" : confidence > 50 ? "Medium" : "High"
  const riskColor = confidence > 75 ? "text-green-600" : confidence > 50 ? "text-yellow-600" : "text-red-600"

  return (
    <div className="space-y-6">
      {/* Main Recommendation */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-6 w-6" />
            AI-Powered Recommendation for {symbol}
          </CardTitle>
          <CardDescription>
            Based on sentiment analysis, technical indicators, and machine learning models
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-4">
                <Badge className={`${details.color} text-white text-lg px-4 py-2`}>
                  <IconComponent className="h-5 w-5 mr-2" />
                  {recommendation}
                </Badge>
              </div>
              <div className="text-2xl font-bold mb-2">Confidence: {confidence}%</div>
              <Progress value={confidence} className="mb-4" />
              <div className={`text-sm font-medium ${riskColor}`}>Risk Level: {riskLevel}</div>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Analysis Summary</h4>
              <p className="text-sm text-gray-600 mb-4">{details.description}</p>
              <h4 className="font-semibold mb-2">Recommended Action</h4>
              <p className="text-sm">{details.action}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Factor Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Decision Factors
          </CardTitle>
          <CardDescription>Breakdown of factors contributing to the recommendation</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Object.entries(factors).map(([key, factor]) => (
              <div key={key} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium">{factor.name}</span>
                    <Badge variant="outline">{factor.signal}</Badge>
                  </div>
                  <div className="flex items-center gap-4">
                    <Progress value={factor.score} className="flex-1" />
                    <span className="text-sm font-medium w-12">{factor.score.toFixed(0)}%</span>
                    <span className="text-xs text-gray-500 w-16">Weight: {factor.weight}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Risk Assessment */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            Risk Assessment
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-lg font-semibold mb-1">Market Risk</div>
              <div className={riskColor}>{riskLevel}</div>
              <Progress value={100 - confidence} className="mt-2" />
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold mb-1">Volatility</div>
              <div className="text-yellow-600">Medium</div>
              <Progress value={60} className="mt-2" />
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold mb-1">Liquidity</div>
              <div className="text-green-600">High</div>
              <Progress value={85} className="mt-2" />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Disclaimer */}
      <Alert>
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          <strong>Disclaimer:</strong> This recommendation is generated by AI analysis and should not be considered as
          financial advice. Always conduct your own research and consider consulting with a financial advisor before
          making investment decisions. Past performance does not guarantee future results.
        </AlertDescription>
      </Alert>
    </div>
  )
}
