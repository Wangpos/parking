"use client"

import { useEffect, useRef } from "react"
import { Card } from "@/components/ui/card"
import { Map, MapPin } from "lucide-react"
import { Badge } from "@/components/ui/badge"

export function ParkingMap() {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<any>(null)

  // Thimphu, Bhutan coordinates with parking zones
  const zones = [
    { 
      id: "A1", 
      name: "Main Entrance North",
      slots: 24, 
      occupied: 18, 
      occupancy: 75,
      location: "Clock Tower Square",
      coordinates: { lat: 27.4728, lng: 89.6393 }
    },
    { 
      id: "A2", 
      name: "Main Entrance South",
      slots: 24, 
      occupied: 12, 
      occupancy: 50,
      location: "Centenary Farmers Market",
      coordinates: { lat: 27.4712, lng: 89.6388 }
    },
    { 
      id: "B1", 
      name: "Building B East",
      slots: 32, 
      occupied: 8, 
      occupancy: 25,
      location: "Motithang Area",
      coordinates: { lat: 27.4850, lng: 89.6350 }
    },
    { 
      id: "B2", 
      name: "Building B West",
      slots: 32, 
      occupied: 28, 
      occupancy: 88,
      location: "Tashichho Dzong",
      coordinates: { lat: 27.4750, lng: 89.6330 }
    },
    { 
      id: "C1", 
      name: "Underground",
      slots: 48, 
      occupied: 35, 
      occupancy: 73,
      location: "Memorial Chorten",
      coordinates: { lat: 27.4770, lng: 89.6430 }
    },
    { 
      id: "C2", 
      name: "VIP Zone",
      slots: 16, 
      occupied: 12, 
      occupancy: 75,
      location: "Buddha Dordenma",
      coordinates: { lat: 27.4920, lng: 89.6700 }
    },
  ]

  useEffect(() => {
    let timer: NodeJS.Timeout | null = null
    
    if (typeof window !== 'undefined' && mapRef.current && !mapInstanceRef.current) {
      // Add small delay to ensure DOM is fully ready
      timer = setTimeout(() => {
        import('leaflet').then((module) => {
          const L = module.default
          // Check if map container already has a map instance
          const container = mapRef.current!
          if ((container as any)._leaflet_id) {
            return
          }

        // Create map centered on Thimphu, Bhutan
        const map = L.map(container, {
          center: [27.4728, 89.6393], // Thimphu coordinates
          zoom: 13,
          zoomControl: true,
        })

        mapInstanceRef.current = map

        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '© OpenStreetMap contributors',
          maxZoom: 19,
        }).addTo(map)

        // Add custom markers for each parking zone
        zones.forEach((zone) => {
          const occupancyColor = 
            zone.occupancy >= 80 ? '#ef4444' : 
            zone.occupancy >= 60 ? '#eab308' : 
            '#22c55e'

          const markerHtml = `
            <div style="
              width: 40px;
              height: 40px;
              background-color: ${occupancyColor};
              border: 3px solid white;
              border-radius: 50%;
              display: flex;
              align-items: center;
              justify-content: center;
              font-weight: bold;
              color: white;
              box-shadow: 0 4px 6px rgba(0,0,0,0.3);
              font-size: 12px;
            ">
              ${zone.id}
            </div>
          `

          const icon = L.divIcon({
            html: markerHtml,
            className: '',
            iconSize: [40, 40],
            iconAnchor: [20, 20],
          })

          const marker = L.marker([zone.coordinates.lat, zone.coordinates.lng], { icon }).addTo(map)

          // Add popup with zone details
          const popupContent = `
            <div style="min-width: 180px;">
              <div style="font-weight: bold; font-size: 14px; margin-bottom: 4px;">Zone ${zone.id}</div>
              <div style="font-size: 12px; color: #666; margin-bottom: 8px;">${zone.name}</div>
              <div style="font-size: 11px; color: #888; margin-bottom: 8px; display: flex; align-items: center; gap: 4px;">
                📍 ${zone.location}
              </div>
              <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px;">
                <span>Occupied:</span>
                <span style="font-weight: bold;">${zone.occupied}/${zone.slots}</span>
              </div>
              <div style="display: flex; justify-content: space-between; font-size: 12px;">
                <span>Occupancy:</span>
                <span style="font-weight: bold; color: ${occupancyColor};">${zone.occupancy}%</span>
              </div>
            </div>
          `

          marker.bindPopup(popupContent)
        })

        // Add location marker for Thimphu city center
        const cityMarkerHtml = `
          <div style="
            width: 30px;
            height: 30px;
            background-color: #3b82f6;
            border: 3px solid white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
          ">
            📍
          </div>
        `

        const cityIcon = L.divIcon({
          html: cityMarkerHtml,
          className: '',
          iconSize: [30, 30],
          iconAnchor: [15, 15],
        })

        L.marker([27.4728, 89.6393], { icon: cityIcon })
          .addTo(map)
          .bindPopup('<div style="font-weight: bold;">Thimphu City Center</div>')
        
        // Force map to recalculate size after initialization
        setTimeout(() => {
          map.invalidateSize()
        }, 100)
        })
      }, 100) // Small delay
    }

    return () => {
      if (timer) clearTimeout(timer)
      if (mapInstanceRef.current) {
        try {
          mapInstanceRef.current.remove()
        } catch (error) {
          console.error('Error removing map:', error)
        }
        mapInstanceRef.current = null
      }
    }
  }, [])

  // Leaflet CSS is now imported globally in layout.tsx

  const getOccupancyColor = (occupancy: number) => {
    if (occupancy >= 80) return "bg-red-500"
    if (occupancy >= 60) return "bg-yellow-500"
    return "bg-green-500"
  }

  const getOccupancyBorder = (occupancy: number) => {
    if (occupancy >= 80) return "border-red-500"
    if (occupancy >= 60) return "border-yellow-500"
    return "border-green-500"
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground mb-2">Interactive Zone Map - Thimphu, Bhutan</h1>
          <p className="text-muted-foreground">Real-time parking availability across Thimphu city</p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <Card className="bg-gradient-to-br from-green-50 to-white border-border p-4">
          <p className="text-xs text-muted-foreground mb-1">Total Zones</p>
          <p className="text-3xl font-bold text-foreground">{zones.length}</p>
        </Card>
        <Card className="bg-gradient-to-br from-blue-50 to-white border-border p-4">
          <p className="text-xs text-muted-foreground mb-1">Total Capacity</p>
          <p className="text-3xl font-bold text-foreground">{zones.reduce((sum, z) => sum + z.slots, 0)}</p>
        </Card>
        <Card className="bg-gradient-to-br from-purple-50 to-white border-border p-4">
          <p className="text-xs text-muted-foreground mb-1">Avg Occupancy</p>
          <p className="text-3xl font-bold text-primary">
            {Math.round(zones.reduce((sum, z) => sum + z.occupancy, 0) / zones.length)}%
          </p>
        </Card>
      </div>

      <Card className="bg-card border-border p-8">
        <h2 className="text-lg font-semibold text-foreground mb-6 flex items-center gap-2">
          <Map className="w-5 h-5 text-primary" />
          Live Map View - Thimphu, Bhutan
        </h2>

        {/* Leaflet Map */}
        <div 
          ref={mapRef} 
          className="rounded-xl border-2 border-gray-300 mb-6 overflow-hidden shadow-lg" 
          style={{ height: "500px", width: "100%" }}
        ></div>

        {/* Legend */}
        <div className="flex items-center justify-center gap-8 mb-6 p-4 bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-green-500 border-2 border-white shadow"></div>
            <span className="text-sm font-medium">Low (&lt;60%)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-yellow-500 border-2 border-white shadow"></div>
            <span className="text-sm font-medium">Medium (60-80%)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-red-500 border-2 border-white shadow"></div>
            <span className="text-sm font-medium">High (&gt;80%)</span>
          </div>
        </div>

        {/* Zone Details Grid */}
        <div className="grid grid-cols-3 gap-4">
          {zones.map((zone) => (
            <Card key={zone.id} className={`border-2 ${getOccupancyBorder(zone.occupancy)} hover:shadow-lg transition-all p-4`}>
              <div className="flex items-start justify-between mb-3">
                <div>
                  <p className="text-lg font-bold text-foreground">Zone {zone.id}</p>
                  <p className="text-xs text-muted-foreground">{zone.name}</p>
                </div>
                <Badge className={`${getOccupancyColor(zone.occupancy)} text-white border-0`}>
                  {zone.occupancy}%
                </Badge>
              </div>
              <div className="flex items-center gap-1 text-xs text-muted-foreground mb-2">
                <MapPin className="w-3 h-3" />
                <span>{zone.location}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Occupied:</span>
                <span className="font-bold">{zone.occupied}/{zone.slots}</span>
              </div>
              <div className="w-full bg-secondary rounded-full h-2 mt-2">
                <div
                  className={`h-2 ${getOccupancyColor(zone.occupancy)} rounded-full transition-all`}
                  style={{ width: `${zone.occupancy}%` }}
                ></div>
              </div>
            </Card>
          ))}
        </div>
      </Card>
    </div>
  )
}
