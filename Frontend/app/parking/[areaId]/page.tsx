"use client"

import { useParams, useRouter } from "next/navigation"
import { ArrowLeft, MapPin, Clock, Car, AlertCircle, Navigation } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ParkingMap } from "@/components/parking-map"

interface ParkingSlot {
  slotId: string
  status: "free" | "occupied"
  vehicleNumber?: string
  entryTime?: string
  duration?: string
  vehicleType?: string
}

export default function ParkingAreaDetailPage() {
  const params = useParams()
  const router = useRouter()
  const areaId = params.areaId as string

  // Mock data - In production, this would come from an API
  const parkingAreaData = {
    A1: {
      name: "Main Entrance - North",
      location: "Clock Tower Square, Thimphu",
      floor: "Ground",
      coordinates: "27.4728° N, 89.6393° E",
      totalSlots: 24,
      slots: generateSlots(24, 18),
    },
    A2: {
      name: "Main Entrance - South",
      location: "Centenary Farmers Market, Thimphu",
      floor: "Ground",
      coordinates: "27.4712° N, 89.6388° E",
      totalSlots: 24,
      slots: generateSlots(24, 12),
    },
    B1: {
      name: "Building B - East Wing",
      location: "Motithang Area, Thimphu",
      floor: "Level 1",
      coordinates: "27.4850° N, 89.6350° E",
      totalSlots: 32,
      slots: generateSlots(32, 8),
    },
    B2: {
      name: "Building B - West Wing",
      location: "Tashichho Dzong, Thimphu",
      floor: "Level 1",
      coordinates: "27.4750° N, 89.6330° E",
      totalSlots: 32,
      slots: generateSlots(32, 28),
    },
    C1: {
      name: "Underground Parking - Level 1",
      location: "Memorial Chorten, Thimphu",
      floor: "B1",
      coordinates: "27.4770° N, 89.6430° E",
      totalSlots: 40,
      slots: generateSlots(40, 15),
    },
    C2: {
      name: "Underground Parking - Level 2",
      location: "Buddha Dordenma, Thimphu",
      floor: "B2",
      coordinates: "27.4920° N, 89.6700° E",
      totalSlots: 40,
      slots: generateSlots(40, 35),
    },
  }

  // Deterministic pseudo-random function to avoid hydration mismatch
  function seededRandom(seed: number): number {
    const x = Math.sin(seed) * 10000
    return x - Math.floor(x)
  }

  function generateSlots(total: number, occupied: number): ParkingSlot[] {
    const slots: ParkingSlot[] = []
    const vehicleNumbers = ["ABC-123", "XYZ-789", "DEF-456", "GHI-012", "JKL-345", "MNO-678", "PQR-901", "STU-234"]
    
    for (let i = 1; i <= total; i++) {
      const isOccupied = i <= occupied
      if (isOccupied) {
        // Use deterministic seeded random based on slot index
        const seed = i * 1000 + areaId.charCodeAt(0) * 100 + areaId.charCodeAt(1)
        const entryHour = Math.floor(seededRandom(seed) * 12) + 1
        const entryMinute = Math.floor(seededRandom(seed + 1) * 60)
        const durationMinutes = Math.floor(seededRandom(seed + 2) * 180) + 10
        const hours = Math.floor(durationMinutes / 60)
        const minutes = durationMinutes % 60
        
        slots.push({
          slotId: `${areaId}${i}`,
          status: "occupied",
          vehicleNumber: vehicleNumbers[Math.floor(seededRandom(seed + 3) * vehicleNumbers.length)],
          entryTime: `${entryHour}:${entryMinute.toString().padStart(2, '0')} ${seededRandom(seed + 4) > 0.5 ? 'AM' : 'PM'}`,
          duration: hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m`,
          vehicleType: seededRandom(seed + 5) > 0.3 ? "Car" : "SUV",
        })
      } else {
        slots.push({
          slotId: `${areaId}${i}`,
          status: "free",
        })
      }
    }
    return slots
  }

  const area = parkingAreaData[areaId as keyof typeof parkingAreaData]

  if (!area) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <Card className="bg-slate-800/50 border-slate-700 text-white">
          <CardContent className="p-6">
            <AlertCircle className="w-12 h-12 mx-auto mb-4 text-red-500" />
            <p className="text-center">Parking area not found</p>
            <Button onClick={() => router.back()} className="mt-4 w-full">
              Go Back
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  const occupiedSlots = area.slots.filter(s => s.status === "occupied").length
  const freeSlots = area.slots.filter(s => s.status === "free").length
  const occupancyRate = Math.round((occupiedSlots / area.totalSlots) * 100)

  // Parse coordinates - handle both East/West longitude
  const parseCoordinates = (coords: string) => {
    const parts = coords.split(',')
    const lat = parseFloat(parts[0].replace('°', '').replace('N', '').replace('S', '').trim())
    const lngValue = parseFloat(parts[1].replace('°', '').replace('W', '').replace('E', '').trim())
    // Check if West (negative) or East (positive)
    const lng = coords.includes('W') ? -lngValue : lngValue
    return { lat, lng }
  }

  const coords = parseCoordinates(area.coordinates)
  const mapLocation = [{
    id: areaId,
    name: area.name,
    lat: coords.lat,
    lng: coords.lng,
    available: freeSlots,
    total: area.totalSlots,
    category: area.floor,
  }]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-slate-700/50 bg-slate-900/80 backdrop-blur-xl">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Button
              onClick={() => router.back()}
              variant="ghost"
              className="text-slate-300 hover:text-white hover:bg-slate-800"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="border-purple-500/50 text-purple-400">
                Zone {areaId}
              </Badge>
              <Badge className={`${
                occupancyRate >= 80 ? 'bg-red-500' : occupancyRate >= 60 ? 'bg-yellow-500' : 'bg-green-500'
              }`}>
                {occupancyRate}% Full
              </Badge>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Area Info Card */}
        <Card className="mb-6 bg-slate-800/50 border-slate-700 backdrop-blur-xl">
          <CardHeader>
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-4">
                <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl flex items-center justify-center text-3xl">
                  🅿️
                </div>
                <div>
                  <CardTitle className="text-2xl text-white mb-2">{area.name}</CardTitle>
                  <div className="flex items-center gap-2 text-slate-400 text-sm mb-2">
                    <MapPin className="w-4 h-4" />
                    <span>{area.location}</span>
                  </div>
                  <Badge variant="outline" className="border-slate-600 text-slate-300">
                    {area.floor}
                  </Badge>
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-slate-700/30 rounded-lg p-4 text-center">
                <div className="text-3xl font-bold text-white">{area.totalSlots}</div>
                <div className="text-sm text-slate-400 mt-1">Total Slots</div>
              </div>
              <div className="bg-green-500/20 border border-green-500/30 rounded-lg p-4 text-center">
                <div className="text-3xl font-bold text-green-400">{freeSlots}</div>
                <div className="text-sm text-slate-400 mt-1">Available</div>
              </div>
              <div className="bg-red-500/20 border border-red-500/30 rounded-lg p-4 text-center">
                <div className="text-3xl font-bold text-red-400">{occupiedSlots}</div>
                <div className="text-sm text-slate-400 mt-1">Occupied</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Location Map */}
        <Card className="mb-6 bg-slate-800/50 border-slate-700 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <MapPin className="w-5 h-5" />
              Location Map
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[450px] w-full rounded-lg overflow-hidden bg-gray-100 border-2 border-gray-200">
              <ParkingMap
                locations={mapLocation}
                center={[coords.lat, coords.lng]}
                zoom={15}
                selectedLocation={areaId}
              />
            </div>
            <p className="text-xs text-slate-400 mt-2 text-center">
              📍 {area.coordinates} • Use Ctrl + Scroll to zoom
            </p>
          </CardContent>
        </Card>

        {/* Parking Map */}
        <Card className="mb-6 bg-slate-800/50 border-slate-700 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Car className="w-5 h-5" />
              Parking Map
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="mb-4 flex items-center gap-4 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-green-500 rounded"></div>
                <span className="text-slate-300">Free</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-red-500 rounded"></div>
                <span className="text-slate-300">Occupied</span>
              </div>
            </div>
            
            <div className="grid grid-cols-6 md:grid-cols-8 lg:grid-cols-12 gap-3">
              {area.slots.map((slot) => (
                <div
                  key={slot.slotId}
                  className={`aspect-square rounded-lg flex items-center justify-center font-bold text-sm cursor-pointer transition-all hover:scale-105 border-2 ${
                    slot.status === "free"
                      ? "border-green-500 text-green-400 hover:bg-green-500/10"
                      : "border-red-500 text-red-400 hover:bg-red-500/10"
                  }`}
                  title={slot.status === "occupied" ? `${slot.vehicleNumber} - ${slot.duration}` : "Available"}
                >
                  {slot.slotId.replace(areaId, '')}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Detailed Slot Information */}
        <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Clock className="w-5 h-5" />
              Slot Details
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              {area.slots.map((slot) => (
                <div
                  key={slot.slotId}
                  className={`p-4 rounded-lg border ${
                    slot.status === "free"
                      ? "bg-green-500/10 border-green-500/30"
                      : "bg-red-500/10 border-red-500/30"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-12 h-12 rounded-lg flex items-center justify-center font-bold ${
                          slot.status === "free" ? "bg-green-500" : "bg-red-500"
                        } text-white`}
                      >
                        {slot.slotId.replace(areaId, '')}
                      </div>
                      <div>
                        <div className="font-semibold text-white">Slot {slot.slotId}</div>
                        {slot.status === "occupied" ? (
                          <div className="text-sm text-slate-400 space-y-1 mt-1">
                            <div className="flex items-center gap-2">
                              <Car className="w-3 h-3" />
                              <span>{slot.vehicleNumber}</span>
                              <span className="text-slate-500">•</span>
                              <span>{slot.vehicleType}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <Clock className="w-3 h-3" />
                              <span>Entry: {slot.entryTime}</span>
                              <span className="text-slate-500">•</span>
                              <span>Duration: {slot.duration}</span>
                            </div>
                          </div>
                        ) : (
                          <div className="text-sm text-green-400 mt-1">Available for parking</div>
                        )}
                      </div>
                    </div>
                    <Badge
                      className={`${
                        slot.status === "free"
                          ? "bg-green-500 hover:bg-green-600"
                          : "bg-red-500 hover:bg-red-600"
                      }`}
                    >
                      {slot.status === "free" ? "FREE" : "OCCUPIED"}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
