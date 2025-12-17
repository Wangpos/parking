"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { MapPin, Navigation2, ArrowRight, Car, Clock, CheckCircle2, Shield, Map } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ParkingMap } from "@/components/parking-map"

interface ParkingArea {
  id: string
  name: string
  location: string
  coordinates: string
  slots: number
  occupied: number
  category: "outdoor" | "covered" | "underground"
  floor: string
}

export default function PublicParkingView() {
  const router = useRouter()
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedCategory, setSelectedCategory] = useState<string>("all")
  const [showMap, setShowMap] = useState(false)

  const areas: ParkingArea[] = [
    {
      id: "A1",
      name: "Main Entrance - North",
      location: "123 Main Street, North Wing",
      coordinates: "40.7128° N, 74.0060° W",
      slots: 24,
      occupied: 18,
      category: "outdoor",
      floor: "Ground",
    },
    {
      id: "A2",
      name: "Main Entrance - South",
      location: "123 Main Street, South Wing",
      coordinates: "40.7125° N, 74.0062° W",
      slots: 24,
      occupied: 12,
      category: "outdoor",
      floor: "Ground",
    },
    {
      id: "B1",
      name: "Building B - East Wing",
      location: "Building B, East Side",
      coordinates: "40.7130° N, 74.0058° W",
      slots: 32,
      occupied: 8,
      category: "covered",
      floor: "Level 1",
    },
    {
      id: "B2",
      name: "Building B - West Wing",
      location: "Building B, West Side",
      coordinates: "40.7132° N, 74.0065° W",
      slots: 32,
      occupied: 28,
      category: "covered",
      floor: "Level 1",
    },
    {
      id: "C1",
      name: "Underground Parking - Level 1",
      location: "Main Building Basement",
      coordinates: "40.7127° N, 74.0061° W",
      slots: 40,
      occupied: 15,
      category: "underground",
      floor: "B1",
    },
    {
      id: "C2",
      name: "Underground Parking - Level 2",
      location: "Main Building Basement",
      coordinates: "40.7127° N, 74.0061° W",
      slots: 40,
      occupied: 35,
      category: "underground",
      floor: "B2",
    },
  ]

  const filteredAreas = areas.filter((area) => {
    const matchesSearch =
      area.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      area.location.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === "all" || area.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const getOccupancyColor = (percentage: number) => {
    if (percentage < 50) return "text-green-500"
    if (percentage < 80) return "text-yellow-500"
    return "text-red-500"
  }

  const getAvailabilityBadge = (available: number) => {
    if (available > 10) return <Badge className="bg-green-500/20 text-green-400 border-green-500/50">High Availability</Badge>
    if (available > 5) return <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/50">Moderate</Badge>
    if (available > 0) return <Badge className="bg-orange-500/20 text-orange-400 border-orange-500/50">Limited</Badge>
    return <Badge className="bg-red-500/20 text-red-400 border-red-500/50">Full</Badge>
  }

  const totalSlots = areas.reduce((sum, area) => sum + area.slots, 0)
  const totalOccupied = areas.reduce((sum, area) => sum + area.occupied, 0)
  const totalAvailable = totalSlots - totalOccupied

  // Convert coordinates to lat/lng for map
  const parseCoordinates = (coords: string) => {
    const parts = coords.split(',')
    const lat = parseFloat(parts[0].replace('°', '').replace('N', '').replace('S', '').trim())
    const lng = parseFloat(parts[1].replace('°', '').replace('W', '').replace('E', '').trim())
    return { lat: lat, lng: lng * (coords.includes('W') ? -1 : 1) }
  }

  const mapLocations = filteredAreas.map((area) => {
    const coords = parseCoordinates(area.coordinates)
    return {
      id: area.id,
      name: area.name,
      lat: coords.lat,
      lng: coords.lng,
      available: area.slots - area.occupied,
      total: area.slots,
      category: area.category,
    }
  })

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Animated background elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" />
          <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse delay-1000" />
        </div>

        {/* Header */}
        <header className="relative z-10 border-b border-slate-700/50 bg-slate-900/50 backdrop-blur-xl">
          <div className="container mx-auto px-4 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl flex items-center justify-center shadow-lg">
                <Car className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Smart Parking</h1>
                <p className="text-sm text-slate-400">Find Your Perfect Spot</p>
              </div>
            </div>
            <Button
              onClick={() => router.push("/login")}
              variant="outline"
              className="border-purple-500/50 text-purple-400 hover:bg-purple-500/10"
            >
              <Shield className="w-4 h-4 mr-2" />
              Admin Login
            </Button>
          </div>
        </header>

        {/* Stats Section */}
        <div className="relative z-10 container mx-auto px-4 py-12">
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Real-Time Parking Availability
            </h2>
            <p className="text-lg text-slate-300 max-w-2xl mx-auto">
              Find available parking spaces instantly with our smart monitoring system
            </p>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <Card className="bg-gradient-to-br from-green-500/10 to-emerald-500/5 border-green-500/30 backdrop-blur-xl transform hover:scale-105 transition-transform">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-400 mb-1">Available Spaces</p>
                    <p className="text-4xl font-bold text-green-400">{totalAvailable}</p>
                  </div>
                  <div className="w-16 h-16 bg-green-500/20 rounded-2xl flex items-center justify-center">
                    <CheckCircle2 className="w-8 h-8 text-green-400" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-blue-500/10 to-cyan-500/5 border-blue-500/30 backdrop-blur-xl transform hover:scale-105 transition-transform">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-400 mb-1">Total Capacity</p>
                    <p className="text-4xl font-bold text-blue-400">{totalSlots}</p>
                  </div>
                  <div className="w-16 h-16 bg-blue-500/20 rounded-2xl flex items-center justify-center">
                    <Car className="w-8 h-8 text-blue-400" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-purple-500/10 to-pink-500/5 border-purple-500/30 backdrop-blur-xl transform hover:scale-105 transition-transform">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-400 mb-1">Occupancy Rate</p>
                    <p className="text-4xl font-bold text-purple-400">
                      {Math.round((totalOccupied / totalSlots) * 100)}%
                    </p>
                  </div>
                  <div className="w-16 h-16 bg-purple-500/20 rounded-2xl flex items-center justify-center">
                    <Clock className="w-8 h-8 text-purple-400" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Filters */}
          <div className="flex flex-col md:flex-row gap-4 mb-8">
            <div className="flex-1">
              <Input
                type="text"
                placeholder="Search parking areas..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="bg-slate-800/50 border-slate-700 text-white placeholder:text-slate-500 h-12"
              />
            </div>
            <div className="flex gap-2">
              <Button
                variant={selectedCategory === "all" ? "default" : "outline"}
                onClick={() => setSelectedCategory("all")}
                className={selectedCategory === "all" ? "bg-purple-500 hover:bg-purple-600" : "border-slate-700 text-slate-300"}
              >
                All Areas
              </Button>
              <Button
                variant={selectedCategory === "outdoor" ? "default" : "outline"}
                onClick={() => setSelectedCategory("outdoor")}
                className={selectedCategory === "outdoor" ? "bg-purple-500 hover:bg-purple-600" : "border-slate-700 text-slate-300"}
              >
                Outdoor
              </Button>
              <Button
                variant={selectedCategory === "covered" ? "default" : "outline"}
                onClick={() => setSelectedCategory("covered")}
                className={selectedCategory === "covered" ? "bg-purple-500 hover:bg-purple-600" : "border-slate-700 text-slate-300"}
              >
                Covered
              </Button>
              <Button
                variant={selectedCategory === "underground" ? "default" : "outline"}
                onClick={() => setSelectedCategory("underground")}
                className={selectedCategory === "underground" ? "bg-purple-500 hover:bg-purple-600" : "border-slate-700 text-slate-300"}
              >
                Underground
              </Button>
              <Button
                variant={showMap ? "default" : "outline"}
                onClick={() => setShowMap(!showMap)}
                className={showMap ? "bg-purple-500 hover:bg-purple-600" : "border-slate-700 text-slate-300"}
              >
                <Map className="w-4 h-4 mr-2" />
                {showMap ? "Hide Map" : "Show Map"}
              </Button>
            </div>
          </div>

          {/* Map View */}
          {showMap && (
            <Card className="mb-8 bg-slate-900/80 border-slate-700/50 backdrop-blur-xl overflow-hidden">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <MapPin className="w-5 h-5" />
                  Parking Areas Map
                </CardTitle>
                <CardDescription className="text-slate-400">
                  Click on markers to see parking area information
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[500px] rounded-lg overflow-hidden">
                  <ParkingMap
                    locations={mapLocations}
                    onMarkerClick={(id) => router.push(`/parking/${id}`)}
                  />
                </div>
              </CardContent>
            </Card>
          )}

          {/* Parking Areas Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAreas.map((area) => {
              const available = area.slots - area.occupied
              const occupancyPercentage = (area.occupied / area.slots) * 100

              return (
                <Card
                  key={area.id}
                  className="bg-slate-900/80 border-slate-700/50 backdrop-blur-xl hover:border-purple-500/50 transition-all duration-300 transform hover:scale-105 hover:shadow-2xl hover:shadow-purple-500/20"
                >
                  <CardHeader>
                    <div className="flex items-start justify-between mb-2">
                      <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl flex items-center justify-center shadow-lg">
                        <MapPin className="w-6 h-6 text-white" />
                      </div>
                      {getAvailabilityBadge(available)}
                    </div>
                    <CardTitle className="text-white text-xl">{area.name}</CardTitle>
                    <CardDescription className="text-slate-400">{area.location}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
                      <div className="text-center flex-1">
                        <p className="text-3xl font-bold text-green-400">{available}</p>
                        <p className="text-sm text-slate-400 mt-1">Available</p>
                      </div>
                      <div className="w-px h-12 bg-slate-700" />
                      <div className="text-center flex-1">
                        <p className="text-3xl font-bold text-slate-300">{area.slots}</p>
                        <p className="text-sm text-slate-400 mt-1">Total</p>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-400">Occupancy</span>
                        <span className={`font-semibold ${getOccupancyColor(occupancyPercentage)}`}>
                          {Math.round(occupancyPercentage)}%
                        </span>
                      </div>
                      <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-purple-500 to-blue-500 transition-all duration-500"
                          style={{ width: `${occupancyPercentage}%` }}
                        />
                      </div>
                    </div>

                    {/* Parking Slot Map */}
                    <div className="bg-slate-800/30 rounded-lg p-3 border border-slate-700/50">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-xs font-semibold text-slate-300">Parking Map</span>
                        <div className="flex items-center gap-3 text-xs">
                          <div className="flex items-center gap-1">
                            <div className="w-2 h-2 rounded-sm bg-green-500"></div>
                            <span className="text-slate-400">Free</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <div className="w-2 h-2 rounded-sm bg-red-500"></div>
                            <span className="text-slate-400">Occupied</span>
                          </div>
                        </div>
                      </div>
                      <div className="grid grid-cols-6 gap-2">
                        {Array.from({ length: 12 }).map((_, i) => {
                          const slotNumber = i + 1
                          const isOccupied = i < Math.round((area.occupied / area.slots) * 12)
                          return (
                            <div
                              key={`${area.id}-slot-${i}`}
                              className={`relative aspect-[3/4] rounded-lg border-2 flex items-center justify-center text-xs font-bold transition-all cursor-pointer hover:scale-110 ${
                                isOccupied 
                                  ? 'bg-red-500/20 border-red-500/50 text-red-400 hover:bg-red-500/30' 
                                  : 'bg-green-500/20 border-green-500/50 text-green-400 hover:bg-green-500/30'
                              }`}
                              title={`Slot ${area.id}-${slotNumber}: ${isOccupied ? "Occupied" : "Available"}`}
                            >
                              <div className="absolute top-0.5 left-0.5 text-[8px] opacity-60">{area.id}</div>
                              <span>{slotNumber}</span>
                            </div>
                          )
                        })}
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-2">
                      <Badge variant="outline" className="border-slate-600 text-slate-300">
                        {area.floor}
                      </Badge>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-purple-400 hover:text-purple-300 hover:bg-purple-500/10"
                        onClick={() => router.push(`/parking/${area.id}`)}
                      >
                        <Navigation2 className="w-4 h-4 mr-1" />
                        Navigate
                        <ArrowRight className="w-4 h-4 ml-1" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>

          {filteredAreas.length === 0 && (
            <div className="text-center py-12">
              <p className="text-slate-400 text-lg">No parking areas found matching your criteria.</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <footer className="relative z-10 border-t border-slate-700/50 bg-slate-900/50 backdrop-blur-xl mt-12">
          <div className="container mx-auto px-4 py-6">
            <div className="flex flex-col md:flex-row items-center justify-between gap-4">
              <p className="text-slate-400 text-sm">
                © 2025 Smart Parking System. Real-time updates every 30 seconds.
              </p>
              <div className="flex items-center gap-2 text-sm text-slate-400">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                <span>System Online</span>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  )
}
