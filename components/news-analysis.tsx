"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Newspaper, ExternalLink, TrendingUp, TrendingDown, Clock } from "lucide-react"

// Mock news data
const mockNewsData = {
  AAPL: [
    {
      title: "Apple Reports Strong Q4 Earnings, Beats Revenue Expectations",
      summary:
        "Apple Inc. reported quarterly revenue of $89.5 billion, surpassing analyst expectations of $87.2 billion. iPhone sales remained robust despite market headwinds.",
      sentiment: 0.78,
      source: "Financial Times",
      timestamp: "2 hours ago",
      url: "#",
      impact: "High",
    },
    {
      title: "New iPhone AI Features Drive Consumer Interest",
      summary:
        "Apple's latest AI-powered features in iOS are generating significant consumer interest, with early adoption rates exceeding expectations.",
      sentiment: 0.65,
      source: "TechCrunch",
      timestamp: "4 hours ago",
      url: "#",
      impact: "Medium",
    },
    {
      title: "Supply Chain Concerns May Impact Q1 Production",
      summary:
        "Industry analysts warn that ongoing supply chain disruptions could affect Apple's production targets for the first quarter of 2024.",
      sentiment: 0.32,
      source: "Reuters",
      timestamp: "6 hours ago",
      url: "#",
      impact: "Medium",
    },
  ],
  TSLA: [
    {
      title: "Tesla Delivery Numbers Fall Short of Q4 Expectations",
      summary:
        "Tesla reported 435,000 vehicle deliveries in Q4, missing analyst estimates of 450,000 units. Production challenges cited as primary factor.",
      sentiment: 0.25,
      source: "Bloomberg",
      timestamp: "1 hour ago",
      url: "#",
      impact: "High",
    },
    {
      title: "Autopilot Technology Receives Major Safety Update",
      summary:
        "Tesla's latest Autopilot update includes enhanced safety features and improved object detection capabilities, addressing previous regulatory concerns.",
      sentiment: 0.72,
      source: "The Verge",
      timestamp: "3 hours ago",
      url: "#",
      impact: "Medium",
    },
    {
      title: "Competition Intensifies in Electric Vehicle Market",
      summary:
        "Traditional automakers are rapidly expanding their EV offerings, creating increased competition for Tesla's market share.",
      sentiment: 0.38,
      source: "Wall Street Journal",
      timestamp: "5 hours ago",
      url: "#",
      impact: "High",
    },
  ],
  GOOGL: [
    {
      title: "Google Cloud Revenue Surges 35% Year-over-Year",
      summary:
        "Alphabet's cloud division reported strong growth, with revenue reaching $8.4 billion in the latest quarter, driven by AI and enterprise adoption.",
      sentiment: 0.75,
      source: "CNBC",
      timestamp: "2 hours ago",
      url: "#",
      impact: "High",
    },
    {
      title: "Bard AI Chatbot Gains New Capabilities",
      summary:
        "Google's Bard AI assistant receives significant updates, including improved reasoning capabilities and integration with Google Workspace.",
      sentiment: 0.68,
      source: "Ars Technica",
      timestamp: "4 hours ago",
      url: "#",
      impact: "Medium",
    },
    {
      title: "Regulatory Scrutiny Increases for Search Dominance",
      summary:
        "European regulators are considering additional measures to address Google's search market dominance, potentially impacting future revenue.",
      sentiment: 0.35,
      source: "Financial Times",
      timestamp: "7 hours ago",
      url: "#",
      impact: "Medium",
    },
  ],
}

interface NewsAnalysisProps {
  symbol: string
}

export default function NewsAnalysis({ symbol }: NewsAnalysisProps) {
  const newsData = mockNewsData[symbol] || mockNewsData["AAPL"]

  const getSentimentColor = (sentiment: number) => {
    if (sentiment > 0.6) return "text-green-600"
    if (sentiment > 0.4) return "text-yellow-600"
    return "text-red-600"
  }

  const getSentimentIcon = (sentiment: number) => {
    return sentiment > 0.5 ? TrendingUp : TrendingDown
  }

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case "High":
        return "bg-red-100 text-red-800"
      case "Medium":
        return "bg-yellow-100 text-yellow-800"
      case "Low":
        return "bg-green-100 text-green-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const averageSentiment = newsData.reduce((sum, news) => sum + news.sentiment, 0) / newsData.length

  return (
    <div className="space-y-6">
      {/* News Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Newspaper className="h-5 w-5" />
            News Sentiment Summary for {symbol}
          </CardTitle>
          <CardDescription>Analysis of recent news articles and their potential market impact</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold mb-1">{(averageSentiment * 100).toFixed(0)}%</div>
              <div className={`text-sm font-medium ${getSentimentColor(averageSentiment)}`}>Average Sentiment</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold mb-1">{newsData.length}</div>
              <div className="text-sm text-gray-600">Recent Articles</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold mb-1">{newsData.filter((n) => n.impact === "High").length}</div>
              <div className="text-sm text-gray-600">High Impact Stories</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* News Articles */}
      <div className="space-y-4">
        {newsData.map((article, index) => {
          const SentimentIcon = getSentimentIcon(article.sentiment)
          return (
            <Card key={index}>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg mb-2">{article.title}</h3>
                    <p className="text-gray-600 text-sm mb-3">{article.summary}</p>
                  </div>
                  <div className="ml-4 text-right">
                    <div
                      className={`flex items-center gap-1 text-sm font-medium ${getSentimentColor(article.sentiment)}`}
                    >
                      <SentimentIcon className="h-4 w-4" />
                      {(article.sentiment * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Badge variant="outline" className="text-xs">
                      {article.source}
                    </Badge>
                    <Badge className={`text-xs ${getImpactColor(article.impact)}`}>{article.impact} Impact</Badge>
                    <div className="flex items-center gap-1 text-xs text-gray-500">
                      <Clock className="h-3 w-3" />
                      {article.timestamp}
                    </div>
                  </div>
                  <Button variant="ghost" size="sm" className="text-xs">
                    <ExternalLink className="h-3 w-3 mr-1" />
                    Read More
                  </Button>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* News Impact Analysis */}
      <Card>
        <CardHeader>
          <CardTitle>Market Impact Analysis</CardTitle>
          <CardDescription>How recent news may affect stock performance</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-semibold mb-2 text-green-600">Positive Catalysts</h4>
                <ul className="text-sm space-y-1">
                  {newsData
                    .filter((n) => n.sentiment > 0.5)
                    .map((n, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <TrendingUp className="h-3 w-3 mt-1 text-green-600" />
                        <span>{n.title.substring(0, 60)}...</span>
                      </li>
                    ))}
                </ul>
              </div>
              <div>
                <h4 className="font-semibold mb-2 text-red-600">Risk Factors</h4>
                <ul className="text-sm space-y-1">
                  {newsData
                    .filter((n) => n.sentiment <= 0.5)
                    .map((n, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <TrendingDown className="h-3 w-3 mt-1 text-red-600" />
                        <span>{n.title.substring(0, 60)}...</span>
                      </li>
                    ))}
                </ul>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
