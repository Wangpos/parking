"use client"

import { BarChart3, AlertCircle, Clock, Map, Settings, Home, TrendingUp, MapPin } from "lucide-react"

interface SidebarProps {
  readonly activeSection: string
  readonly setActiveSection: (section: string) => void
}

export function Sidebar({ activeSection, setActiveSection }: SidebarProps) {
  const menuItems = [
    { id: "monitoring", label: "Dashboard", icon: Home },
    { id: "areas", label: "Parking Areas", icon: MapPin },
    { id: "violations", label: "Violations", icon: AlertCircle },
    { id: "analytics", label: "Analytics", icon: BarChart3 },
    { id: "duration", label: "Duration Tracker", icon: Clock },
    { id: "map", label: "Zone Map", icon: Map },
  ]

  return (
    <aside className="w-64 bg-slate-900/50 border-r border-slate-700/50 backdrop-blur-xl">
      <div className="p-6">
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
              onClick={() => setActiveSection(id)}
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

      <div className="absolute bottom-6 left-6 right-6">
        <button className="w-full flex items-center gap-2 px-4 py-3 rounded-xl text-slate-300 hover:bg-slate-800/50 hover:text-white transition-all transform hover:scale-105">
          <Settings className="w-5 h-5" />
          <span className="text-sm font-medium">Settings</span>
        </button>
      </div>
    </aside>
  )
}
