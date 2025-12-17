"use client"

import { Card } from "@/components/ui/card"
import { AlertTriangle, Clock, MapPin, XCircle, Ban, Timer, ShieldAlert, Car } from "lucide-react"
import { Badge } from "@/components/ui/badge"

interface Violation {
  slot: string
  type: string
  time: string
  severity: "High" | "Medium" | "Low"
  license: string
  description: string
}

interface AreaViolations {
  id: string
  name: string
  location: string
  violations: Violation[]
  totalViolations: number
}

export function ViolationsPanel() {
  const parkingAreas: AreaViolations[] = [
    {
      id: "A1",
      name: "Main Entrance - North",
      location: "123 Main St, North Wing",
      totalViolations: 1,
      violations: [
        {
          slot: "A1-015",
          type: "Expired Duration",
          time: "2 min ago",
          severity: "Medium",
          license: "BP-2024-101",
          description: "Vehicle parked for 8+ hours",
        },
      ],
    },
    {
      id: "A2",
      name: "Main Entrance - South",
      location: "123 Main St, South Wing",
      totalViolations: 0,
      violations: [],
    },
    {
      id: "B1",
      name: "Building B - East Wing",
      location: "Building B, East Side",
      totalViolations: 0,
      violations: [],
    },
    {
      id: "B2",
      name: "Building B - West Wing",
      location: "Building B, West Side",
      totalViolations: 2,
      violations: [
        {
          slot: "B2-008",
          type: "Double Parking",
          time: "5 min ago",
          severity: "High",
          license: "BP-2024-202",
          description: "Vehicle blocking another slot",
        },
        {
          slot: "B2-022",
          type: "Outside Boundary",
          time: "12 min ago",
          severity: "Medium",
          license: "BP-2024-203",
          description: "Vehicle parked over line markers",
        },
      ],
    },
    {
      id: "C1",
      name: "Underground Parking",
      location: "Building C, Basement",
      totalViolations: 0,
      violations: [],
    },
    {
      id: "C2",
      name: "VIP Parking Zone",
      location: "Main Building, Reserved Area",
      totalViolations: 1,
      violations: [
        {
          slot: "C2-005",
          type: "No Valid Permit",
          time: "8 min ago",
          severity: "High",
          license: "BP-2024-301",
          description: "Unauthorized vehicle in VIP zone",
        },
      ],
    },
  ]

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "High":
        return "bg-red-100 text-red-700 border-red-300"
      case "Medium":
        return "bg-yellow-100 text-yellow-700 border-yellow-300"
      case "Low":
        return "bg-blue-100 text-blue-700 border-blue-300"
      default:
        return "bg-gray-100 text-gray-700 border-gray-300"
    }
  }

  const getViolationIcon = (type: string) => {
    switch (type) {
      case "Double Parking":
        return <Car className="w-4 h-4" />
      case "No Valid Permit":
        return <ShieldAlert className="w-4 h-4" />
      case "Expired Duration":
        return <Timer className="w-4 h-4" />
      case "Outside Boundary":
        return <Ban className="w-4 h-4" />
      default:
        return <AlertTriangle className="w-4 h-4" />
    }
  }

  const totalViolations = parkingAreas.reduce((sum, area) => sum + area.violations.length, 0)
  const highSeverity = parkingAreas.reduce(
    (sum, area) => sum + area.violations.filter((v) => v.severity === "High").length,
    0
  )
  const mediumSeverity = parkingAreas.reduce(
    (sum, area) => sum + area.violations.filter((v) => v.severity === "Medium").length,
    0
  )
  const areasWithViolations = parkingAreas.filter((area) => area.violations.length > 0).length

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground mb-2">Violations & Alerts by Area</h1>
          <p className="text-muted-foreground">Real-time monitoring of parking violations across all areas</p>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-red-50 to-white border-border p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-4 h-4 text-red-600" />
            <p className="text-xs text-muted-foreground">Total Violations</p>
          </div>
          <p className="text-3xl font-bold text-red-600">{totalViolations}</p>
        </Card>
        <Card className="bg-gradient-to-br from-orange-50 to-white border-border p-4">
          <div className="flex items-center gap-2 mb-2">
            <XCircle className="w-4 h-4 text-orange-600" />
            <p className="text-xs text-muted-foreground">High Severity</p>
          </div>
          <p className="text-3xl font-bold text-orange-600">{highSeverity}</p>
        </Card>
        <Card className="bg-gradient-to-br from-yellow-50 to-white border-border p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-4 h-4 text-yellow-600" />
            <p className="text-xs text-muted-foreground">Medium Severity</p>
          </div>
          <p className="text-3xl font-bold text-yellow-600">{mediumSeverity}</p>
        </Card>
        <Card className="bg-gradient-to-br from-blue-50 to-white border-border p-4">
          <div className="flex items-center gap-2 mb-2">
            <MapPin className="w-4 h-4 text-blue-600" />
            <p className="text-xs text-muted-foreground">Areas Affected</p>
          </div>
          <p className="text-3xl font-bold text-blue-600">{areasWithViolations}</p>
        </Card>
      </div>

      {/* Area-based Violations */}
      <div className="grid grid-cols-1 gap-6">
        {parkingAreas.map((area) => (
          <Card
            key={area.id}
            className={`border-border overflow-hidden transition-all ${
              area.violations.length > 0
                ? "bg-white hover:shadow-lg border-l-4 border-l-red-500"
                : "bg-gray-50 opacity-75"
            }`}
          >
            <div
              className={`p-5 border-b border-border ${
                area.violations.length > 0
                  ? "bg-gradient-to-r from-red-50 to-transparent"
                  : "bg-gradient-to-r from-gray-100 to-transparent"
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-bold text-foreground">{area.name}</h3>
                    <Badge variant="outline" className="text-xs">
                      Area {area.id}
                    </Badge>
                    {area.violations.length > 0 ? (
                      <Badge className="bg-red-100 text-red-700 border-red-200 text-xs font-semibold gap-1">
                        <AlertTriangle className="w-3 h-3" />
                        {area.violations.length} Active Violation{area.violations.length > 1 ? "s" : ""}
                      </Badge>
                    ) : (
                      <Badge className="bg-green-100 text-green-700 border-green-200 text-xs">✓ No Violations</Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                    <MapPin className="w-3.5 h-3.5" />
                    <span>{area.location}</span>
                  </div>
                </div>
              </div>
            </div>

            {area.violations.length > 0 ? (
              <div className="divide-y divide-border">
                {area.violations.map((violation) => (
                  <div
                    key={violation.slot}
                    className="p-5 hover:bg-red-50/50 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-start gap-3">
                        <div className="p-2 bg-red-100 rounded-lg text-red-600 mt-1">
                          {getViolationIcon(violation.type)}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <h4 className="font-bold text-foreground">{violation.type}</h4>
                            <Badge className={`border font-medium ${getSeverityColor(violation.severity)}`}>
                              {violation.severity}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground mb-2">{violation.description}</p>
                          <div className="flex items-center gap-6 text-sm">
                            <div className="flex items-center gap-1.5">
                              <span className="text-muted-foreground">Slot:</span>
                              <span className="font-mono font-semibold text-foreground">{violation.slot}</span>
                            </div>
                            <div className="flex items-center gap-1.5">
                              <span className="text-muted-foreground">License:</span>
                              <span className="font-mono font-semibold text-primary">{violation.license}</span>
                            </div>
                            <div className="flex items-center gap-1.5 text-muted-foreground">
                              <Clock className="w-3.5 h-3.5" />
                              <span>{violation.time}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center text-muted-foreground">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-green-100 mb-3">
                  <span className="text-2xl">✓</span>
                </div>
                <p className="text-sm">No violations in this area</p>
              </div>
            )}
          </Card>
        ))}
      </div>
    </div>
  )
}
