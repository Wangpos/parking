"use client"

import { useEffect, useRef } from "react"
import { MapPin } from "lucide-react"

interface ParkingLocation {
  id: string
  name: string
  lat: number
  lng: number
  available: number
  total: number
  category: string
}

interface ParkingMapProps {
  locations: ParkingLocation[]
  center?: [number, number]
  zoom?: number
  onMarkerClick?: (id: string) => void
  selectedLocation?: string
}

export function ParkingMap({
  locations,
  center = [27.4728, 89.6393],
  zoom = 15,
  onMarkerClick,
  selectedLocation,
}: ParkingMapProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<any>(null)
  const markersRef = useRef<any[]>([])

  useEffect(() => {
    if (typeof window === "undefined" || !mapRef.current) return

    // Add a small delay to ensure DOM is fully ready
    const timer = setTimeout(() => {
      const initMap = async () => {
        // Dynamically import Leaflet to avoid SSR issues
        const L = (await import("leaflet")).default
      
      // Fix for default marker icon
      delete (L.Icon.Default.prototype as any)._getIconUrl
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",
        iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
        shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
      })

      if (mapRef.current && !mapInstanceRef.current) {
        // Check if map container already has a map instance
        const container = mapRef.current
        if ((container as any)._leaflet_id) {
          return
        }

        // Initialize map with better controls
        const map = L.map(container, {
          center: center,
          zoom: zoom,
          zoomControl: true,
          scrollWheelZoom: false, // Disable scroll wheel zoom for less sensitivity
          doubleClickZoom: true,
          touchZoom: true,
          dragging: true,
          zoomSnap: 0.5, // Smoother zoom transitions
          zoomDelta: 0.5,
          minZoom: 12,
          maxZoom: 18,
        })

        // Enable scroll wheel zoom only with Ctrl key
        map.on('focus', () => {
          map.scrollWheelZoom.enable()
        })
        map.on('blur', () => {
          map.scrollWheelZoom.disable()
        })

        // Add tile layer
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
          maxZoom: 19,
        }).addTo(map)

        mapInstanceRef.current = map

        // Add markers for each location
        locations.forEach((location) => {
          const occupancyRate = ((location.total - location.available) / location.total) * 100
          const markerColor = occupancyRate >= 80 ? "red" : occupancyRate >= 60 ? "orange" : "green"

          // Create custom icon
          const customIcon = L.divIcon({
            className: "custom-marker",
            html: `
              <div class="relative">
                <div class="w-10 h-10 rounded-full flex items-center justify-center shadow-lg border-4 border-white ${
                  markerColor === "red"
                    ? "bg-red-500"
                    : markerColor === "orange"
                    ? "bg-yellow-500"
                    : "bg-green-500"
                }" style="margin-left: -20px; margin-top: -20px;">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                  </svg>
                </div>
                <div class="absolute top-10 left-1/2 transform -translate-x-1/2 bg-slate-900 text-white px-2 py-1 rounded text-xs whitespace-nowrap font-semibold shadow-lg ${
                  location.id === selectedLocation ? "block" : "hidden"
                }">
                  ${location.available}/${location.total}
                </div>
              </div>
            `,
            iconSize: [40, 40],
            iconAnchor: [20, 20],
          })

          const marker = L.marker([location.lat, location.lng], { icon: customIcon })
            .addTo(map)
            .bindPopup(
              `
              <div class="p-2">
                <h3 class="font-bold text-base mb-2">${location.name}</h3>
                <div class="space-y-1 text-sm">
                  <p><strong>Available:</strong> <span class="text-green-600">${location.available}</span> / ${location.total}</p>
                  <p><strong>Category:</strong> ${location.category}</p>
                  <p><strong>Occupancy:</strong> <span class="${
                    occupancyRate >= 80 ? "text-red-600" : occupancyRate >= 60 ? "text-yellow-600" : "text-green-600"
                  }">${Math.round(occupancyRate)}%</span></p>
                </div>
              </div>
            `,
              { maxWidth: 250 }
            )

          marker.on("click", () => {
            if (onMarkerClick) {
              onMarkerClick(location.id)
            }
          })

          markersRef.current.push(marker)
        })

        // Set up global click handler for popup buttons
        if (onMarkerClick) {
          ;(window as any).handleMarkerClick = (id: string) => {
            onMarkerClick(id)
          }
        }
        }
      }

      initMap()
    }, 100) // Small delay to ensure container is ready

    // Cleanup
    return () => {
      clearTimeout(timer)
      if (mapInstanceRef.current) {
        try {
          mapInstanceRef.current.remove()
        } catch (error) {
          console.error('Error removing map:', error)
        }
        mapInstanceRef.current = null
      }
      markersRef.current = []
    }
  }, [locations, center, zoom, onMarkerClick, selectedLocation])

  // Invalidate map size when container changes
  useEffect(() => {
    if (mapInstanceRef.current) {
      setTimeout(() => {
        mapInstanceRef.current?.invalidateSize()
      }, 100)
    }
  }, [])

  return (
    <div 
      ref={mapRef} 
      className="w-full rounded-lg overflow-hidden"
      style={{ height: '500px', width: '100%' }}
    />
  )
}
