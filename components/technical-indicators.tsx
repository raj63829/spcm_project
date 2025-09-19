"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, TrendingDown, Activity, BarChart3 } from "lucide-react"

interface TechnicalIndicatorsProps {
  data: {
    rsi: number
    sma20: number
    sma50: number
    volume: number
  }
}

export default function TechnicalIndicators({ data }: TechnicalIndicatorsProps) {
  const getRSISignal = (rsi: number) => {
    if (rsi > 70) return { signal: "Overbought", color: "text-red-600", icon: TrendingDown }
    if (rsi < 30) return { signal: "Oversold", color: "text-green-600", icon: TrendingUp }
    return { signal: "Neutral", color: "text-yellow-600", icon: Activity }
  }

  const getSMASignal = (sma20: number, sma50: number) => {
    if (sma20 > sma50) return { signal: "Bullish", color: "text-green-600", icon: TrendingUp }
    return { signal: "Bearish", color: "text-red-600", icon: TrendingDown }
  }

  const rsiSignal = getRSISignal(data.rsi)
  const smaSignal = getSMASignal(data.sma20, data.sma50)

  // Additional technical indicators (mock calculations)
  const macd = {
    value: 2.34,
    signal: 1.89,
    histogram: 0.45,
  }

  const bollinger = {
    upper: data.sma20 * 1.02,
    middle: data.sma20,
    lower: data.sma20 * 0.98,
  }

  return (
    <div className="space-y-6">
      {/* Key Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex items-center gap-2">
              <Activity className="h-5 w-5" />
              RSI
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.rsi.toFixed(1)}</div>
            <div className={`flex items-center gap-1 text-sm ${rsiSignal.color}`}>
              <rsiSignal.icon className="h-4 w-4" />
              {rsiSignal.signal}
            </div>
            <Progress value={data.rsi} className="mt-2" />
            <div className="text-xs text-gray-500 mt-1">{"<30 Oversold | >70 Overbought"}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">SMA 20/50</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-1">
              <div className="text-sm">SMA 20: ${data.sma20.toFixed(2)}</div>
              <div className="text-sm">SMA 50: ${data.sma50.toFixed(2)}</div>
            </div>
            <div className={`flex items-center gap-1 text-sm mt-2 ${smaSignal.color}`}>
              <smaSignal.icon className="h-4 w-4" />
              {smaSignal.signal} Crossover
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">MACD</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-1 text-sm">
              <div>MACD: {macd.value.toFixed(2)}</div>
              <div>Signal: {macd.signal.toFixed(2)}</div>
              <div>Histogram: {macd.histogram.toFixed(2)}</div>
            </div>
            <Badge variant={macd.histogram > 0 ? "default" : "destructive"} className="mt-2">
              {macd.histogram > 0 ? "Bullish" : "Bearish"}
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Volume
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(data.volume / 1000000).toFixed(1)}M</div>
            <div className="text-sm text-gray-600">Above Average</div>
            <Progress value={75} className="mt-2" />
          </CardContent>
        </Card>
      </div>

      {/* Detailed Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Bollinger Bands</CardTitle>
            <CardDescription>Price volatility and support/resistance levels</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center p-2 bg-red-50 rounded">
                <span className="text-sm font-medium">Upper Band</span>
                <span className="font-bold">${bollinger.upper.toFixed(2)}</span>
              </div>
              <div className="flex justify-between items-center p-2 bg-blue-50 rounded">
                <span className="text-sm font-medium">Middle Band (SMA 20)</span>
                <span className="font-bold">${bollinger.middle.toFixed(2)}</span>
              </div>
              <div className="flex justify-between items-center p-2 bg-green-50 rounded">
                <span className="text-sm font-medium">Lower Band</span>
                <span className="font-bold">${bollinger.lower.toFixed(2)}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Technical Summary</CardTitle>
            <CardDescription>Overall technical analysis verdict</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span>RSI Signal</span>
                <Badge variant={data.rsi > 70 ? "destructive" : data.rsi < 30 ? "default" : "secondary"}>
                  {rsiSignal.signal}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span>Moving Average</span>
                <Badge variant={data.sma20 > data.sma50 ? "default" : "destructive"}>{smaSignal.signal}</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span>MACD</span>
                <Badge variant={macd.histogram > 0 ? "default" : "destructive"}>
                  {macd.histogram > 0 ? "Bullish" : "Bearish"}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span>Volume</span>
                <Badge variant="default">High</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
