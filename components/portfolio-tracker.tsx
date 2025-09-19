"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Wallet, Plus, TrendingUp, TrendingDown } from "lucide-react"

// Mock portfolio data
const mockPortfolio = [
  {
    symbol: "AAPL",
    name: "Apple Inc.",
    shares: 50,
    avgPrice: 175.2,
    currentPrice: 185.92,
    value: 9296,
    gainLoss: 536,
    gainLossPercent: 6.11,
    recommendation: "BUY",
  },
  {
    symbol: "TSLA",
    name: "Tesla Inc.",
    shares: 25,
    avgPrice: 265.8,
    currentPrice: 248.5,
    value: 6212.5,
    gainLoss: -432.5,
    gainLossPercent: -6.51,
    recommendation: "HOLD",
  },
  {
    symbol: "GOOGL",
    name: "Alphabet Inc.",
    shares: 30,
    avgPrice: 138.45,
    currentPrice: 142.18,
    value: 4265.4,
    gainLoss: 111.9,
    gainLossPercent: 2.69,
    recommendation: "BUY",
  },
]

export default function PortfolioTracker() {
  const [portfolio, setPortfolio] = useState(mockPortfolio)
  const [newStock, setNewStock] = useState({ symbol: "", shares: "", price: "" })

  const totalValue = portfolio.reduce((sum, stock) => sum + stock.value, 0)
  const totalGainLoss = portfolio.reduce((sum, stock) => sum + stock.gainLoss, 0)
  const totalGainLossPercent = (totalGainLoss / (totalValue - totalGainLoss)) * 100

  const addStock = () => {
    if (newStock.symbol && newStock.shares && newStock.price) {
      const shares = Number.parseInt(newStock.shares)
      const price = Number.parseFloat(newStock.price)
      const currentPrice = price * (1 + (Math.random() - 0.5) * 0.1) // Mock current price

      const stock = {
        symbol: newStock.symbol.toUpperCase(),
        name: `${newStock.symbol.toUpperCase()} Corp.`,
        shares,
        avgPrice: price,
        currentPrice,
        value: shares * currentPrice,
        gainLoss: shares * (currentPrice - price),
        gainLossPercent: ((currentPrice - price) / price) * 100,
        recommendation: Math.random() > 0.5 ? "BUY" : "HOLD",
      }

      setPortfolio([...portfolio, stock])
      setNewStock({ symbol: "", shares: "", price: "" })
    }
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

  return (
    <div className="space-y-6">
      {/* Portfolio Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex items-center gap-2">
              <Wallet className="h-5 w-5" />
              Total Value
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${totalValue.toLocaleString()}</div>
            <div
              className={`flex items-center gap-1 text-sm ${totalGainLoss >= 0 ? "text-green-600" : "text-red-600"}`}
            >
              {totalGainLoss >= 0 ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}$
              {Math.abs(totalGainLoss).toLocaleString()} ({totalGainLossPercent.toFixed(2)}%)
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Holdings</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{portfolio.length}</div>
            <div className="text-sm text-gray-600">Active Positions</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Best Performer</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-lg font-bold">
              {portfolio.reduce((best, stock) => (stock.gainLossPercent > best.gainLossPercent ? stock : best)).symbol}
            </div>
            <div className="text-sm text-green-600">
              +
              {portfolio
                .reduce((best, stock) => (stock.gainLossPercent > best.gainLossPercent ? stock : best))
                .gainLossPercent.toFixed(2)}
              %
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Recommendations</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-lg font-bold text-green-600">
              {portfolio.filter((s) => s.recommendation === "BUY").length} BUY
            </div>
            <div className="text-sm text-gray-600">
              {portfolio.filter((s) => s.recommendation === "HOLD").length} HOLD
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Add New Stock */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Plus className="h-5 w-5" />
            Add New Position
          </CardTitle>
          <CardDescription>Add a new stock to your portfolio</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Input
              placeholder="Stock Symbol"
              value={newStock.symbol}
              onChange={(e) => setNewStock({ ...newStock, symbol: e.target.value })}
            />
            <Input
              placeholder="Shares"
              type="number"
              value={newStock.shares}
              onChange={(e) => setNewStock({ ...newStock, shares: e.target.value })}
            />
            <Input
              placeholder="Avg Price"
              type="number"
              step="0.01"
              value={newStock.price}
              onChange={(e) => setNewStock({ ...newStock, price: e.target.value })}
            />
            <Button onClick={addStock}>Add Position</Button>
          </div>
        </CardContent>
      </Card>

      {/* Portfolio Holdings */}
      <Card>
        <CardHeader>
          <CardTitle>Portfolio Holdings</CardTitle>
          <CardDescription>Your current stock positions and performance</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {portfolio.map((stock, index) => (
              <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center gap-4">
                  <div>
                    <div className="font-semibold">{stock.symbol}</div>
                    <div className="text-sm text-gray-600">{stock.name}</div>
                  </div>
                  <div className="text-sm">
                    <div>{stock.shares} shares</div>
                    <div className="text-gray-600">Avg: ${stock.avgPrice.toFixed(2)}</div>
                  </div>
                </div>

                <div className="text-center">
                  <div className="font-semibold">${stock.currentPrice.toFixed(2)}</div>
                  <div className={`text-sm ${stock.gainLoss >= 0 ? "text-green-600" : "text-red-600"}`}>
                    {stock.gainLoss >= 0 ? "+" : ""}${stock.gainLoss.toFixed(2)}
                  </div>
                </div>

                <div className="text-center">
                  <div className="font-semibold">${stock.value.toLocaleString()}</div>
                  <div className={`text-sm ${stock.gainLossPercent >= 0 ? "text-green-600" : "text-red-600"}`}>
                    {stock.gainLossPercent >= 0 ? "+" : ""}
                    {stock.gainLossPercent.toFixed(2)}%
                  </div>
                </div>

                <Badge className={`${getRecommendationColor(stock.recommendation)} text-white`}>
                  {stock.recommendation}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Portfolio Allocation */}
      <Card>
        <CardHeader>
          <CardTitle>Portfolio Allocation</CardTitle>
          <CardDescription>Distribution of your investments</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {portfolio.map((stock, index) => {
              const percentage = (stock.value / totalValue) * 100
              return (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="font-medium">{stock.symbol}</span>
                    <span className="text-sm text-gray-600">${stock.value.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <Progress value={percentage} className="w-24" />
                    <span className="text-sm font-medium w-12">{percentage.toFixed(1)}%</span>
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
