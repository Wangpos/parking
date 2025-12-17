"use client"

import { Card } from "@/components/ui/card"
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { TrendingUp, BarChart3 } from "lucide-react"

export function AnalyticsSection() {
  const occupancyData = [
    { time: "6:00 AM", occupancy: 15 },
    { time: "8:00 AM", occupancy: 45 },
    { time: "10:00 AM", occupancy: 68 },
    { time: "12:00 PM", occupancy: 82 },
    { time: "2:00 PM", occupancy: 75 },
    { time: "4:00 PM", occupancy: 88 },
    { time: "6:00 PM", occupancy: 92 },
    { time: "8:00 PM", occupancy: 45 },
    { time: "10:00 PM", occupancy: 22 },
  ]

  const violationData = [
    { day: "Mon", violations: 12 },
    { day: "Tue", violations: 8 },
    { day: "Wed", violations: 15 },
    { day: "Thu", violations: 10 },
    { day: "Fri", violations: 18 },
    { day: "Sat", violations: 22 },
    { day: "Sun", violations: 9 },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground mb-2">Analytics & Insights</h1>
        <p className="text-muted-foreground">Comprehensive parking system analytics</p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <Card className="bg-card border-border p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-primary" />
            Occupancy Trend
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={occupancyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(100,100,100,0.1)" />
              <XAxis dataKey="time" stroke="rgba(200,200,200,0.5)" style={{ fontSize: "12px" }} />
              <YAxis stroke="rgba(200,200,200,0.5)" style={{ fontSize: "12px" }} />
              <Tooltip
                contentStyle={{ backgroundColor: "rgba(20,20,30,0.95)", border: "1px solid rgba(100,100,255,0.3)" }}
              />
              <Line type="monotone" dataKey="occupancy" stroke="rgb(82, 165, 255)" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        <Card className="bg-card border-border p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-primary" />
            Weekly Violations
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={violationData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(100,100,100,0.1)" />
              <XAxis dataKey="day" stroke="rgba(200,200,200,0.5)" style={{ fontSize: "12px" }} />
              <YAxis stroke="rgba(200,200,200,0.5)" style={{ fontSize: "12px" }} />
              <Tooltip
                contentStyle={{ backgroundColor: "rgba(20,20,30,0.95)", border: "1px solid rgba(255,80,80,0.3)" }}
              />
              <Bar dataKey="violations" fill="rgb(239, 68, 68)" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <Card className="bg-card border-border p-4">
          <p className="text-xs text-muted-foreground mb-2">Peak Occupancy</p>
          <p className="text-2xl font-bold text-primary">92%</p>
          <p className="text-xs text-muted-foreground mt-2">6:00 PM - 7:00 PM</p>
        </Card>
        <Card className="bg-card border-border p-4">
          <p className="text-xs text-muted-foreground mb-2">Lowest Occupancy</p>
          <p className="text-2xl font-bold text-green-400">15%</p>
          <p className="text-xs text-muted-foreground mt-2">6:00 AM - 7:00 AM</p>
        </Card>
        <Card className="bg-card border-border p-4">
          <p className="text-xs text-muted-foreground mb-2">Total Violations</p>
          <p className="text-2xl font-bold text-red-400">94</p>
          <p className="text-xs text-muted-foreground mt-2">This week</p>
        </Card>
        <Card className="bg-card border-border p-4">
          <p className="text-xs text-muted-foreground mb-2">CO₂ Saved</p>
          <p className="text-2xl font-bold text-accent">2.4T</p>
          <p className="text-xs text-muted-foreground mt-2">This month</p>
        </Card>
      </div>
    </div>
  )
}
