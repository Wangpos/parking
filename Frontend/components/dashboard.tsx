"use client"

import { useState, useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"
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
  const router = useRouter()
  const searchParams = useSearchParams()
  const [activeSection, setActiveSection] = useState("monitoring")

  // Initialize from URL on mount
  useEffect(() => {
    const section = searchParams.get("section")
    if (section) {
      setActiveSection(section)
    }
  }, [])

  // Update URL when section changes
  const handleSectionChange = (section: string) => {
    setActiveSection(section)
    router.push(`/admin?section=${section}`, { scroll: false })
  }

  useEffect(() => {
    const section = searchParams.get("section") || "monitoring"
    if (section !== activeSection) {
      setActiveSection(section)
    }
  }, [searchParams])

  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <Sidebar 
        activeSection={activeSection} 
        setActiveSection={handleSectionChange}
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
      />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
        <main className="flex-1 overflow-auto">
          <div className="p-4 sm:p-6 md:p-8 max-w-7xl mx-auto">
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
