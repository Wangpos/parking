"use client"

import { BarChart3, AlertCircle, Clock, Map, Settings, Home, TrendingUp, MapPin } from "lucide-react"

interface SidebarProps {
  readonly activeSection: string
  readonly setActiveSection: (section: string) => void
  readonly sidebarOpen?: boolean
  readonly setSidebarOpen?: (open: boolean) => void
}

export function Sidebar({ activeSection, setActiveSection, sidebarOpen, setSidebarOpen }: SidebarProps) {
  const menuItems = [
    { id: "monitoring", label: "Dashboard", icon: Home },
    { id: "areas", label: "Parking Areas", icon: MapPin },
    { id: "violations", label: "Violations", icon: AlertCircle },
    { id: "analytics", label: "Analytics", icon: BarChart3 },
    { id: "duration", label: "Duration Tracker", icon: Clock },
    { id: "map", label: "Zone Map", icon: Map },
  ]

  const handleSectionClick = (section: string) => {
    setActiveSection(section)
    if (setSidebarOpen) {
      setSidebarOpen(false)
    }
  }

  return (
    <>
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={() => setSidebarOpen?.(false)}
        />
      )}
      
      <aside className={`
        fixed md:static inset-y-0 left-0 z-50
        w-64 bg-slate-900/95 md:bg-slate-900/50 border-r border-slate-700/50 backdrop-blur-xl
        transform transition-transform duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
      <div className="p-4 sm:p-6">
        <div className="flex items-center gap-2 mb-8">
          <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl flex items-center justify-center shadow-lg">
            <TrendingUp className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-xl text-white">ParkHub</span>
        </div>

        <nav className="space-y-2">
          {menuItems.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => handleSectionClick(id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all transform hover:scale-105 ${
                activeSection === id
                  ? "bg-gradient-to-r from-purple-500 to-blue-500 text-white shadow-lg shadow-purple-500/50"
                  : "text-slate-300 hover:bg-slate-800/50 hover:text-white"
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="text-sm font-medium">{label}</span>
            </button>
          ))}
        </nav>
      </div>

      <div className="absolute bottom-4 sm:bottom-6 left-4 sm:left-6 right-4 sm:right-6">
        <button className="w-full flex items-center gap-2 px-4 py-3 rounded-xl text-slate-300 hover:bg-slate-800/50 hover:text-white transition-all transform hover:scale-105">
          <Settings className="w-5 h-5" />
          <span className="text-sm font-medium">Settings</span>
        </button>
      </div>
    </aside>
    </>
  )
}
