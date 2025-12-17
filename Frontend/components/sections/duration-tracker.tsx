"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Clock, MapPin, Timer, AlertCircle, TrendingUp, DollarSign } from "lucide-react"
import { Badge } from "@/components/ui/badge"

interface Vehicle {
  slot: string
  entry: string
  duration: string
  durationMinutes: number
  status: "Normal" | "Warning" | "Alert"
  license: string
  entryTimestamp: number
}

const HOURLY_RATE = 20 // 20 per hour

interface AreaData {
  id: string
  name: string
  location: string
  vehicles: Vehicle[]
  avgDuration: string
  longestDuration: string
}

export function DurationTracker() {
  const [currentTime, setCurrentTime] = useState(Date.now())

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(Date.now())
    }, 1000) // Update every second

    return () => clearInterval(timer)
  }, [])

  const calculateDuration = (entryTimestamp: number) => {
    const now = currentTime
    const durationMs = now - entryTimestamp
    const totalMinutes = Math.floor(durationMs / 60000)
    const hours = Math.floor(totalMinutes / 60)
    const minutes = totalMinutes % 60
    return { hours, minutes, totalMinutes }
  }

  const calculateFee = (totalMinutes: number) => {
    const hours = totalMinutes / 60
    return Math.ceil(hours * HOURLY_RATE)
  }

  const getStatus = (totalMinutes: number): "Normal" | "Warning" | "Alert" => {
    if (totalMinutes >= 420) return "Alert" // 7+ hours
    if (totalMinutes >= 300) return "Warning" // 5+ hours
    return "Normal"
  }

  // Create entry timestamps (simulating cars that parked at different times today)
  const now = new Date()
  const createTimestamp = (hoursAgo: number, minutesAgo: number) => {
    return now.getTime() - (hoursAgo * 60 * 60 * 1000) - (minutesAgo * 60 * 1000)
  }

  const parkingAreas: AreaData[] = [
    {
      id: "A1",
      name: "Main Entrance - North",
      location: "123 Main St, North Wing",
      avgDuration: "3h 45m",
      longestDuration: "6h 20m",
      vehicles: [
        { slot: "A1-001", entry: "08:30 AM", duration: "4h 22m", durationMinutes: 262, status: "Normal", license: "BP-2024-101", entryTimestamp: createTimestamp(4, 22) },
        { slot: "A1-005", entry: "09:15 AM", duration: "3h 37m", durationMinutes: 217, status: "Normal", license: "BP-2024-102", entryTimestamp: createTimestamp(3, 37) },
        { slot: "A1-012", entry: "06:45 AM", duration: "6h 07m", durationMinutes: 367, status: "Warning", license: "BP-2024-103", entryTimestamp: createTimestamp(6, 7) },
        { slot: "A1-018", entry: "11:20 AM", duration: "1h 32m", durationMinutes: 92, status: "Normal", license: "BP-2024-104", entryTimestamp: createTimestamp(1, 32) },
      ],
    },
    {
      id: "A2",
      name: "Main Entrance - South",
      location: "123 Main St, South Wing",
      avgDuration: "2h 30m",
      longestDuration: "4h 15m",
      vehicles: [
        { slot: "A2-003", entry: "10:00 AM", duration: "2h 52m", durationMinutes: 172, status: "Normal", license: "BP-2024-105", entryTimestamp: createTimestamp(2, 52) },
        { slot: "A2-008", entry: "09:30 AM", duration: "3h 22m", durationMinutes: 202, status: "Normal", license: "BP-2024-106", entryTimestamp: createTimestamp(3, 22) },
        { slot: "A2-015", entry: "08:00 AM", duration: "4h 52m", durationMinutes: 292, status: "Normal", license: "BP-2024-107", entryTimestamp: createTimestamp(4, 52) },
      ],
    },
    {
      id: "B1",
      name: "Building B - East Wing",
      location: "Building B, East Side",
      avgDuration: "1h 45m",
      longestDuration: "2h 40m",
      vehicles: [
        { slot: "B1-002", entry: "11:30 AM", duration: "1h 22m", durationMinutes: 82, status: "Normal", license: "BP-2024-108", entryTimestamp: createTimestamp(1, 22) },
        { slot: "B1-006", entry: "10:45 AM", duration: "2h 07m", durationMinutes: 127, status: "Normal", license: "BP-2024-109", entryTimestamp: createTimestamp(2, 7) },
      ],
    },
    {
      id: "B2",
      name: "Building B - West Wing",
      location: "Building B, West Side",
      avgDuration: "5h 15m",
      longestDuration: "8h 30m",
      vehicles: [
        { slot: "B2-010", entry: "05:20 AM", duration: "7h 32m", durationMinutes: 452, status: "Alert", license: "BP-2024-110", entryTimestamp: createTimestamp(7, 32) },
        { slot: "B2-014", entry: "04:45 AM", duration: "8h 07m", durationMinutes: 487, status: "Alert", license: "BP-2024-111", entryTimestamp: createTimestamp(8, 7) },
        { slot: "B2-020", entry: "07:30 AM", duration: "5h 22m", durationMinutes: 322, status: "Warning", license: "BP-2024-112", entryTimestamp: createTimestamp(5, 22) },
        { slot: "B2-025", entry: "09:00 AM", duration: "3h 52m", durationMinutes: 232, status: "Normal", license: "BP-2024-113", entryTimestamp: createTimestamp(3, 52) },
      ],
    },
    {
      id: "C1",
      name: "Underground Parking",
      location: "Building C, Basement",
      avgDuration: "4h 20m",
      longestDuration: "7h 15m",
      vehicles: [
        { slot: "C1-008", entry: "06:00 AM", duration: "6h 52m", durationMinutes: 412, status: "Warning", license: "BP-2024-114", entryTimestamp: createTimestamp(6, 52) },
        { slot: "C1-015", entry: "08:30 AM", duration: "4h 22m", durationMinutes: 262, status: "Normal", license: "BP-2024-115", entryTimestamp: createTimestamp(4, 22) },
        { slot: "C1-022", entry: "09:45 AM", duration: "3h 07m", durationMinutes: 187, status: "Normal", license: "BP-2024-116", entryTimestamp: createTimestamp(3, 7) },
      ],
    },
    {
      id: "C2",
      name: "VIP Parking Zone",
      location: "Main Building, Reserved Area",
      avgDuration: "6h 30m",
      longestDuration: "9h 45m",
      vehicles: [
        { slot: "C2-001", entry: "04:00 AM", duration: "8h 52m", durationMinutes: 532, status: "Alert", license: "BP-VIP-001", entryTimestamp: createTimestamp(8, 52) },
        { slot: "C2-003", entry: "07:15 AM", duration: "5h 37m", durationMinutes: 337, status: "Warning", license: "BP-VIP-002", entryTimestamp: createTimestamp(5, 37) },
      ],
    },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Alert":
        return "bg-red-100 text-red-700 border-red-300"
      case "Warning":
        return "bg-yellow-100 text-yellow-700 border-yellow-300"
      default:
        return "bg-green-100 text-green-700 border-green-300"
    }
  }

  const getStatusIcon = (status: string) => {
    if (status === "Alert" || status === "Warning") {
      return <AlertCircle className="w-3 h-3" />
    }
    return <Clock className="w-3 h-3" />
  }

  const totalVehicles = parkingAreas.reduce((sum, area) => sum + area.vehicles.length, 0)
  const alertCount = parkingAreas.reduce(
    (sum, area) => sum + area.vehicles.filter((v) => v.status === "Alert").length,
    0
  )
  const warningCount = parkingAreas.reduce(
    (sum, area) => sum + area.vehicles.filter((v) => v.status === "Warning").length,
    0
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground mb-2">Duration Tracker by Area</h1>
          <p className="text-muted-foreground">Monitor vehicle parking duration across all parking areas</p>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-blue-50 to-white border-border p-4">
          <div className="flex items-center gap-2 mb-2">
            <Clock className="w-4 h-4 text-blue-600" />
            <p className="text-xs text-muted-foreground">Total Vehicles</p>
          </div>
          <p className="text-3xl font-bold text-foreground">{totalVehicles}</p>
        </Card>
        <Card className="bg-gradient-to-br from-green-50 to-white border-border p-4">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-4 h-4 text-green-600" />
            <p className="text-xs text-muted-foreground">Normal Status</p>
          </div>
          <p className="text-3xl font-bold text-green-600">{totalVehicles - alertCount - warningCount}</p>
        </Card>
        <Card className="bg-gradient-to-br from-yellow-50 to-white border-border p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="w-4 h-4 text-yellow-600" />
            <p className="text-xs text-muted-foreground">Warnings</p>
          </div>
          <p className="text-3xl font-bold text-yellow-600">{warningCount}</p>
        </Card>
        <Card className="bg-gradient-to-br from-red-50 to-white border-border p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="w-4 h-4 text-red-600" />
            <p className="text-xs text-muted-foreground">Alerts</p>
          </div>
          <p className="text-3xl font-bold text-red-600">{alertCount}</p>
        </Card>
      </div>

      {/* Area-based Duration Cards */}
      <div className="grid grid-cols-1 gap-6">
        {parkingAreas.map((area) => (
          <Card key={area.id} className="bg-white border-border overflow-hidden hover:shadow-lg transition-all">
            <div className="p-5 border-b border-border bg-gradient-to-r from-primary/5 to-transparent">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-bold text-foreground">{area.name}</h3>
                    <Badge variant="outline" className="text-xs">Area {area.id}</Badge>
                    <Badge className="bg-blue-100 text-blue-700 border-blue-200 text-xs">
                      {area.vehicles.length} vehicles
                    </Badge>
                  </div>
                  <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                    <MapPin className="w-3.5 h-3.5" />
                    <span>{area.location}</span>
                  </div>
                </div>
                <div className="flex gap-4 text-sm">
                  <div className="text-right">
                    <div className="flex items-center gap-1.5 text-muted-foreground mb-1">
                      <Timer className="w-3.5 h-3.5" />
                      <span className="text-xs">Avg Duration</span>
                    </div>
                    <p className="font-bold text-foreground">{area.avgDuration}</p>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center gap-1.5 text-muted-foreground mb-1">
                      <Clock className="w-3.5 h-3.5" />
                      <span className="text-xs">Longest</span>
                    </div>
                    <p className="font-bold text-orange-600">{area.longestDuration}</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-secondary/50">
                  <tr>
                    <th className="px-6 py-3 text-left text-muted-foreground font-medium text-xs">Slot ID</th>
                    <th className="px-6 py-3 text-left text-muted-foreground font-medium text-xs">License Plate</th>
                    <th className="px-6 py-3 text-left text-muted-foreground font-medium text-xs">Entry Time</th>
                    <th className="px-6 py-3 text-left text-muted-foreground font-medium text-xs">Duration</th>
                    <th className="px-6 py-3 text-left text-muted-foreground font-medium text-xs">Parking Fee</th>
                    <th className="px-6 py-3 text-left text-muted-foreground font-medium text-xs">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {area.vehicles.map((vehicle) => {
                    const { hours, minutes, totalMinutes } = calculateDuration(vehicle.entryTimestamp)
                    const fee = calculateFee(totalMinutes)
                    const liveStatus = getStatus(totalMinutes)
                    
                    return (
                      <tr key={vehicle.slot} className="hover:bg-secondary/30 transition-colors">
                        <td className="px-6 py-4">
                          <span className="text-foreground font-mono font-semibold">{vehicle.slot}</span>
                        </td>
                        <td className="px-6 py-4">
                          <span className="text-foreground font-mono">{vehicle.license}</span>
                        </td>
                        <td className="px-6 py-4 text-muted-foreground">{vehicle.entry}</td>
                        <td className="px-6 py-4">
                          <span className="text-foreground font-semibold tabular-nums">
                            {hours}h {minutes.toString().padStart(2, '0')}m
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-1.5">
                            <DollarSign className="w-3.5 h-3.5 text-green-600" />
                            <span className="text-foreground font-bold">{fee}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <Badge className={`border font-medium gap-1 ${getStatusColor(liveStatus)}`}>
                            {getStatusIcon(liveStatus)}
                            {liveStatus}
                          </Badge>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
