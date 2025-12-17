"use client"

import { ParkingCircle, AlertTriangle, TrendingUp, Clock } from "lucide-react"

export function MetricsGrid() {
  const metrics = [
    { 
      label: "Total Capacity", 
      value: "176", 
      subtext: "parking spaces",
      change: "0%", 
      icon: ParkingCircle, 
      iconColor: "text-blue-600",
      iconBg: "bg-blue-100",
      accentColor: "border-l-blue-500"
    },
    { 
      label: "Currently Parked", 
      value: "113", 
      subtext: "vehicles now",
      change: "+12%", 
      icon: TrendingUp, 
      iconColor: "text-orange-600",
      iconBg: "bg-orange-100",
      accentColor: "border-l-orange-500",
      trend: "up"
    },
    { 
      label: "Available Spaces", 
      value: "63", 
      subtext: "slots free",
      change: "-12%", 
      icon: ParkingCircle, 
      iconColor: "text-green-600",
      iconBg: "bg-green-100",
      accentColor: "border-l-green-500",
      trend: "down"
    },
    { 
      label: "Active Issues", 
      value: "3", 
      subtext: "violations",
      change: "-5", 
      icon: AlertTriangle, 
      iconColor: "text-red-600",
      iconBg: "bg-red-100",
      accentColor: "border-l-red-500",
      trend: "down"
    },
    { 
      label: "Utilization Rate", 
      value: "64.2%", 
      subtext: "avg occupancy",
      change: "+2.3%", 
      icon: TrendingUp, 
      iconColor: "text-purple-600",
      iconBg: "bg-purple-100",
      accentColor: "border-l-purple-500",
      trend: "up"
    },
    { 
      label: "Parking Duration", 
      value: "2.4h", 
      subtext: "average stay",
      change: "-0.2h", 
      icon: Clock, 
      iconColor: "text-indigo-600",
      iconBg: "bg-indigo-100",
      accentColor: "border-l-indigo-500",
      trend: "down"
    },
  ]

  const getTrendBadgeStyle = (trend?: string) => {
    if (trend === 'up') return 'bg-green-100 text-green-700'
    if (trend === 'down') return 'bg-blue-100 text-blue-700'
    return 'bg-gray-100 text-gray-600'
  }

  return (
    <div className="grid grid-cols-3 gap-4">
      {metrics.map((metric) => {
        const Icon = metric.icon
        
        return (
          <div 
            key={metric.label} 
            className={`bg-white rounded-xl border-l-4 ${metric.accentColor} border-t border-r border-b border-gray-200 p-5 hover:shadow-lg transition-all duration-300 group`}
          >
            <div className="flex items-start justify-between mb-4">
              <div className={`w-12 h-12 ${metric.iconBg} rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform`}>
                <Icon className={`w-6 h-6 ${metric.iconColor}`} />
              </div>
              {metric.change && (
                <div className={`text-xs font-bold px-2.5 py-1 rounded-full ${getTrendBadgeStyle(metric.trend)}`}>
                  {metric.change}
                </div>
              )}
            </div>
            
            <div>
              <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
                {metric.label}
              </div>
              <div className="text-3xl font-bold text-gray-900 mb-1 group-hover:scale-105 transition-transform inline-block">
                {metric.value}
              </div>
              <div className="text-xs text-gray-400">
                {metric.subtext}
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}


