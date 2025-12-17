"use client"

import { useRouter } from "next/navigation"
import { MapPin, Navigation, Building2, ArrowRight } from "lucide-react"

export function ParkingAreas() {
  const router = useRouter()
  const areas = [
    {
      id: "A1",
      name: "Main Entrance - North",
      location: "123 Main Street, North Wing",
      coordinates: "40.7128° N, 74.0060° W",
      slots: 24,
      occupied: 18,
      violations: 1,
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
      violations: 0,
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
      violations: 0,
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
      violations: 2,
      category: "covered",
      floor: "Level 1",
    },
    {
      id: "C1",
      name: "Underground Parking",
      location: "Building C, Basement",
      coordinates: "40.7126° N, 74.0061° W",
      slots: 48,
      occupied: 35,
      violations: 0,
      category: "underground",
      floor: "B1",
    },
    {
      id: "C2",
      name: "VIP Parking Zone",
      location: "Main Building, Reserved Area",
      coordinates: "40.7129° N, 74.0059° W",
      slots: 16,
      occupied: 12,
      violations: 0,
      category: "vip",
      floor: "Ground",
    },
  ]

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "vip":
        return "⭐"
      case "underground":
        return "🚇"
      case "covered":
        return "🏢"
      default:
        return "🅿️"
    }
  }

  const getOccupancyColor = (occupied: number, slots: number) => {
    const rate = (occupied / slots) * 100
    if (rate >= 80) return "bg-red-500"
    if (rate >= 60) return "bg-yellow-500"
    return "bg-green-500"
  }

  const getOccupancyBadgeColor = (occupancyRate: number) => {
    if (occupancyRate >= 80) return 'bg-red-500'
    if (occupancyRate >= 60) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between border-b-2 border-gray-200 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Parking Areas Overview</h1>
          <p className="text-sm text-gray-500 mt-1">Detailed availability and location information</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors flex items-center gap-2">
          <Navigation className="w-4 h-4" />
          Open Map View
        </button>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-5 text-white">
          <div className="text-sm font-medium opacity-90 mb-1">Total Areas</div>
          <div className="text-4xl font-bold">{areas.length}</div>
        </div>
        <div className="bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl p-5 text-white">
          <div className="text-sm font-medium opacity-90 mb-1">Total Capacity</div>
          <div className="text-4xl font-bold">{areas.reduce((sum, a) => sum + a.slots, 0)}</div>
        </div>
        <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl p-5 text-white">
          <div className="text-sm font-medium opacity-90 mb-1">In Use</div>
          <div className="text-4xl font-bold">{areas.reduce((sum, a) => sum + a.occupied, 0)}</div>
        </div>
        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-5 text-white">
          <div className="text-sm font-medium opacity-90 mb-1">Available</div>
          <div className="text-4xl font-bold">
            {areas.reduce((sum, a) => sum + (a.slots - a.occupied), 0)}
          </div>
        </div>
      </div>

      {/* Areas Grid */}
      <div className="grid grid-cols-2 gap-5">
        {areas.map((area) => {
          const occupancyRate = Math.round((area.occupied / area.slots) * 100)
          const available = area.slots - area.occupied

          return (
            <div
              key={area.id}
              className="bg-white rounded-2xl border-2 border-gray-200 overflow-hidden hover:shadow-2xl hover:border-blue-400 transition-all duration-300"
            >
              {/* Header with gradient */}
              <div className="bg-gradient-to-r from-gray-50 to-gray-100 p-5 border-b-2 border-gray-200">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="text-4xl">{getCategoryIcon(area.category)}</div>
                    <div>
                      <h3 className="text-lg font-bold text-gray-900">{area.name}</h3>
                      <div className="flex items-center gap-1.5 text-xs text-gray-500 mt-0.5">
                        <Building2 className="w-3 h-3" />
                        <span>{area.floor}</span>
                        <span className="mx-1">•</span>
                        <span>Zone {area.id}</span>
                      </div>
                    </div>
                  </div>
                  <div className={`px-3 py-1.5 rounded-full text-xs font-bold text-white ${getOccupancyBadgeColor(occupancyRate)}`}>
                    {occupancyRate}%
                  </div>
                </div>
                <div className="flex items-center gap-1.5 text-xs text-gray-600">
                  <MapPin className="w-3.5 h-3.5" />
                  <span>{area.location}</span>
                </div>
              </div>

              {/* Stats Section */}
              <div className="p-5">
                <div className="grid grid-cols-3 gap-3 mb-5">
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-gray-900">{area.slots}</div>
                    <div className="text-xs text-gray-500 font-medium mt-1">Total</div>
                  </div>
                  <div className="text-center p-3 bg-red-50 rounded-lg">
                    <div className="text-2xl font-bold text-red-600">{area.occupied}</div>
                    <div className="text-xs text-gray-500 font-medium mt-1">Occupied</div>
                  </div>
                  <div className="text-center p-3 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">{available}</div>
                    <div className="text-xs text-gray-500 font-medium mt-1">Free</div>
                  </div>
                </div>

                {/* Progress bar */}
                <div className="mb-5">
                  <div className="h-4 bg-gray-200 rounded-full overflow-hidden relative">
                    <div
                      className={`h-full ${getOccupancyColor(area.occupied, area.slots)} transition-all duration-1000 relative`}
                      style={{ width: `${occupancyRate}%` }}
                    >
                      <div className="absolute inset-0 bg-gradient-to-r from-transparent to-white/30"></div>
                    </div>
                  </div>
                </div>

                {/* Car Grid */}
                <div className="bg-gray-50 rounded-lg p-3 border-2 border-gray-200">
                  <div className="grid grid-cols-12 gap-1.5">
                    {Array.from({ length: 24 }).map((_, i) => {
                      const isOccupied = i < Math.round((area.occupied / area.slots) * 24)
                      const slotNumber = i + 1
                      return (
                        <div key={`${area.id}-vis-${i}`}>
                          <div className={`w-full aspect-square rounded border-2 flex items-center justify-center font-bold text-[10px] ${
                            isOccupied 
                              ? 'border-red-500 bg-red-50 text-red-700' 
                              : 'border-green-500 bg-green-50 text-green-700'
                          }`}>
                            {slotNumber}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              </div>

              {/* Footer */}
              <div className="px-5 py-3 bg-gray-50 border-t-2 border-gray-200 flex items-center justify-between">
                <div className="flex items-center gap-3 text-xs text-gray-600">
                  {area.violations > 0 && (
                    <span className="px-2 py-1 bg-red-100 text-red-700 rounded font-medium border border-red-300">
                      {area.violations} Issue{area.violations > 1 ? 's' : ''}
                    </span>
                  )}
                  <span className="font-mono text-gray-700">{area.coordinates}</span>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
