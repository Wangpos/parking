"use client"

import { MapPin } from "lucide-react"

export function RealTimeMonitoring() {
  const parkingAreas = [
    { id: "A1", location: "Main Entrance - North", slots: 24, occupied: 18, status: "high" },
    { id: "A2", location: "Main Entrance - South", slots: 24, occupied: 12, status: "medium" },
    { id: "B1", location: "Building B - East Wing", slots: 32, occupied: 8, status: "low" },
    { id: "B2", location: "Building B - West Wing", slots: 32, occupied: 28, status: "high" },
  ]

  const getProgressColor = (status: string) => {
    if (status === "high") return "bg-gradient-to-r from-red-500 to-orange-500"
    if (status === "medium") return "bg-gradient-to-r from-yellow-500 to-amber-500"
    return "bg-gradient-to-r from-green-500 to-emerald-500"
  }

  const getStatusText = (occupied: number, slots: number) => {
    const rate = (occupied / slots) * 100
    if (rate >= 80) return { text: "Almost Full", color: "text-red-400", bg: "bg-red-500/20 border-red-500/50" }
    if (rate >= 60) return { text: "Filling Up", color: "text-yellow-400", bg: "bg-yellow-500/20 border-yellow-500/50" }
    return { text: "Available", color: "text-green-400", bg: "bg-green-500/20 border-green-500/50" }
  }

  return (
    <div className="space-y-5">
      <div className="flex items-end justify-between border-b-2 border-slate-700/50 pb-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Live Parking Status</h2>
          <p className="text-sm text-slate-400 mt-1">Real-time availability across all zones</p>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          <span>Updated now</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-5">
        {parkingAreas.map((area) => {
          const occupancyRate = Math.round((area.occupied / area.slots) * 100)
          const available = area.slots - area.occupied
          const statusInfo = getStatusText(area.occupied, area.slots)

          return (
            <div
              key={area.id}
              className="relative bg-slate-900/80 backdrop-blur-xl rounded-2xl border border-slate-700/50 overflow-hidden hover:shadow-2xl hover:shadow-purple-500/20 transition-all duration-300 group transform hover:scale-105"
            >
              {/* Top Color Bar */}
              <div className={`h-1.5 ${getProgressColor(area.status)}`}></div>

              <div className="p-6">
                {/* Header Section */}
                <div className="flex items-start justify-between mb-5">
                  <div className="flex items-start gap-3">
                    <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center text-white font-bold text-lg shadow-lg shadow-purple-500/30">
                      {area.id}
                    </div>
                    <div>
                      <h3 className="font-bold text-white text-base mb-0.5">{area.location}</h3>
                      <div className="flex items-center gap-1 text-xs text-slate-400">
                        <MapPin className="w-3 h-3" />
                        <span>Zone {area.id}</span>
                      </div>
                    </div>
                  </div>
                  <div className={`px-3 py-1.5 rounded-full text-xs font-semibold border ${statusInfo.bg} ${statusInfo.color}`}>
                    {statusInfo.text}
                  </div>
                </div>

                {/* Stats Row */}
                <div className="grid grid-cols-3 gap-3 mb-5">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-white">{area.slots}</div>
                    <div className="text-xs text-slate-400 font-medium">Total</div>
                  </div>
                  <div className="text-center border-x border-slate-700">
                    <div className="text-2xl font-bold text-red-400">{area.occupied}</div>
                    <div className="text-xs text-slate-400 font-medium">Occupied</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-400">{available}</div>
                    <div className="text-xs text-slate-400 font-medium">Free</div>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mb-5">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-medium text-slate-400">Occupancy</span>
                    <span className="text-sm font-bold text-white">{occupancyRate}%</span>
                  </div>
                  <div className="h-3 bg-slate-800/50 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${getProgressColor(area.status)} transition-all duration-1000 rounded-full relative`}
                      style={{ width: `${occupancyRate}%` }}
                    >
                      <div className="absolute inset-0 bg-white/20 animate-pulse"></div>
                    </div>
                  </div>
                </div>

                {/* Car Grid Visualization */}
                <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/50">
                  <div className="grid grid-cols-8 gap-2">
                    {Array.from({ length: 16 }).map((_, i) => {
                      const isOccupied = i < Math.round((area.occupied / area.slots) * 16)
                      const slotNumber = i + 1
                      return (
                        <div
                          key={`${area.id}-slot-${i}`}
                          title={`Slot ${slotNumber}: ${isOccupied ? "Occupied" : "Available"}`}
                        >
                          <div className={`w-full aspect-square rounded flex items-center justify-center font-semibold text-xs border-2 transition-all ${
                            isOccupied ? 'border-red-500/50 text-red-400 bg-red-500/10' : 'border-green-500/50 text-green-400 bg-green-500/10'
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
              <div className="px-6 py-3 bg-slate-800/50 border-t border-slate-700/50 flex items-center justify-between">
                <div className="flex items-center gap-4 text-xs">
                  <div className="flex items-center gap-1.5">
                    <div className="w-2.5 h-2.5 rounded-full bg-green-500"></div>
                    <span className="text-slate-400">Available</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <div className="w-2.5 h-2.5 rounded-full bg-red-500"></div>
                    <span className="text-slate-400">Occupied</span>
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
