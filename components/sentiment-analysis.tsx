"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { MessageSquare, TrendingUp, TrendingDown, Twitter, Newspaper } from "lucide-react"

// Mock sentiment data
const mockSentimentData = {
  AAPL: {
    sources: [
      { source: "Twitter", sentiment: 0.72, count: 1250, icon: Twitter },
      { source: "News", sentiment: 0.58, count: 45, icon: Newspaper },
      { source: "Reddit", sentiment: 0.65, count: 320, icon: MessageSquare },
    ],
    keywords: ["iPhone", "earnings", "innovation", "growth", "AI"],
    recentMentions: [
      { text: "Apple's new AI features are game-changing!", sentiment: 0.85, source: "Twitter" },
      { text: "Strong quarterly earnings beat expectations", sentiment: 0.78, source: "News" },
      { text: "iPhone sales looking solid this quarter", sentiment: 0.65, source: "Reddit" },
    ],
  },
  TSLA: {
    sources: [
      { source: "Twitter", sentiment: 0.45, count: 2100, icon: Twitter },
      { source: "News", sentiment: 0.38, count: 67, icon: Newspaper },
      { source: "Reddit", sentiment: 0.42, count: 580, icon: MessageSquare },
    ],
    keywords: ["autopilot", "production", "Musk", "delivery", "competition"],
    recentMentions: [
      { text: "Tesla delivery numbers disappointing this quarter", sentiment: 0.25, source: "News" },
      { text: "Autopilot improvements are impressive", sentiment: 0.7, source: "Twitter" },
      { text: "Competition heating up in EV space", sentiment: 0.35, source: "Reddit" },
    ],
  },
  GOOGL: {
    sources: [
      { source: "Twitter", sentiment: 0.62, count: 890, icon: Twitter },
      { source: "News", sentiment: 0.55, count: 38, icon: Newspaper },
      { source: "Reddit", sentiment: 0.58, count: 245, icon: MessageSquare },
    ],
    keywords: ["AI", "search", "cloud", "advertising", "Bard"],
    recentMentions: [
      { text: "Google's AI advancements are impressive", sentiment: 0.75, source: "Twitter" },
      { text: "Cloud revenue growth continues strong", sentiment: 0.68, source: "News" },
      { text: "Search dominance remains unchallenged", sentiment: 0.6, source: "Reddit" },
    ],
  },
}

interface SentimentAnalysisProps {
  symbol: string
  sentimentScore: number
}

export default function SentimentAnalysis({ symbol, sentimentScore }: SentimentAnalysisProps) {
  const data = mockSentimentData[symbol] || mockSentimentData["AAPL"]

  const getSentimentColor = (score: number) => {
    if (score > 0.6) return "text-green-600"
    if (score > 0.4) return "text-yellow-600"
    return "text-red-600"
  }

  const getSentimentLabel = (score: number) => {
    if (score > 0.6) return "Positive"
    if (score > 0.4) return "Neutral"
    return "Negative"
  }

  return (
    <div className="space-y-6">
      {/* Overall Sentiment */}
      <Card>
        <CardHeader>
          <CardTitle>Overall Sentiment Analysis</CardTitle>
          <CardDescription>Aggregated sentiment from multiple sources</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-3xl font-bold mb-2">{(sentimentScore * 100).toFixed(0)}%</div>
              <div className={`text-lg font-semibold ${getSentimentColor(sentimentScore)}`}>
                {getSentimentLabel(sentimentScore)}
              </div>
              <Progress value={sentimentScore * 100} className="mt-2" />
            </div>
            <div className="col-span-2">
              <h4 className="font-semibold mb-2">Trending Keywords</h4>
              <div className="flex flex-wrap gap-2">
                {data.keywords.map((keyword, index) => (
                  <Badge key={index} variant="secondary">
                    {keyword}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Source Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Sentiment by Source</CardTitle>
          <CardDescription>Breakdown of sentiment across different platforms</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {data.sources.map((source, index) => {
              const IconComponent = source.icon
              return (
                <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <IconComponent className="h-5 w-5" />
                    <div>
                      <div className="font-semibold">{source.source}</div>
                      <div className="text-sm text-gray-600">{source.count} mentions</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`text-lg font-semibold ${getSentimentColor(source.sentiment)}`}>
                      {(source.sentiment * 100).toFixed(0)}%
                    </div>
                    <Progress value={source.sentiment * 100} className="w-24" />
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Recent Mentions */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Mentions</CardTitle>
          <CardDescription>Latest sentiment-analyzed mentions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {data.recentMentions.map((mention, index) => (
              <div key={index} className="p-3 border rounded-lg">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-sm">{mention.text}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant="outline" className="text-xs">
                        {mention.source}
                      </Badge>
                      <div className={`flex items-center gap-1 text-xs ${getSentimentColor(mention.sentiment)}`}>
                        {mention.sentiment > 0.5 ? (
                          <TrendingUp className="h-3 w-3" />
                        ) : (
                          <TrendingDown className="h-3 w-3" />
                        )}
                        {getSentimentLabel(mention.sentiment)}
                      </div>
                    </div>
                  </div>
                  <div className={`text-sm font-semibold ${getSentimentColor(mention.sentiment)}`}>
                    {(mention.sentiment * 100).toFixed(0)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
