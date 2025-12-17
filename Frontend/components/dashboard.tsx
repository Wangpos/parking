"use client"

import { useState } from "react"
import { Header } from "./header"
import { Sidebar } from "./sidebar"
import { RealTimeMonitoring } from "./sections/real-time-monitoring"
import { MetricsGrid } from "./sections/metrics-grid"
import { ViolationsPanel } from "./sections/violations-panel"
import { AnalyticsSection } from "./sections/analytics-section"
import { DurationTracker } from "./sections/duration-tracker"
import { ParkingMap } from "./sections/parking-map"
import { ParkingAreas } from "./sections/parking-areas"

export function Dashboard() {
  const [activeSection, setActiveSection] = useState("monitoring")

  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <Sidebar activeSection={activeSection} setActiveSection={setActiveSection} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-auto">
          <div className="p-8 max-w-7xl mx-auto">
            {activeSection === "monitoring" && (
              <div className="space-y-6">
                <RealTimeMonitoring />
                <MetricsGrid />
              </div>
            )}
            {activeSection === "areas" && <ParkingAreas />}
            {activeSection === "violations" && <ViolationsPanel />}
            {activeSection === "analytics" && <AnalyticsSection />}
            {activeSection === "duration" && <DurationTracker />}
            {activeSection === "map" && <ParkingMap />}
          </div>
        </main>
      </div>
    </div>
  )
}
