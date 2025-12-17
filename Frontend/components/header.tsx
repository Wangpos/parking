"use client"

import { Clock, Bell, LogOut } from "lucide-react"
import { useState, useEffect } from "react"
import { useAuth } from "@/contexts/auth-context"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"

export function Header() {
  const [time, setTime] = useState<string>("")
  const { user, logout } = useAuth()
  const router = useRouter()

  useEffect(() => {
    setTime(new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" }))
    const interval = setInterval(() => {
      setTime(new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" }))
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  const handleLogout = () => {
    logout()
    router.push("/")
  }

  return (
    <header className="border-b border-slate-700/50 bg-slate-900/50 backdrop-blur-xl">
      <div className="px-8 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Smart Parking Dashboard</h1>
          <p className="text-sm text-slate-400 mt-1">Real-time AI-powered parking system</p>
        </div>
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2 px-4 py-2 bg-slate-800/50 rounded-lg border border-slate-700">
            <Clock className="w-4 h-4 text-purple-400" />
            <span className="text-sm font-mono text-white">{time}</span>
          </div>
          <button className="p-2 hover:bg-slate-800/50 rounded-lg transition-colors text-slate-400 hover:text-white relative">
            <Bell className="w-5 h-5" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
          </button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                <Avatar className="h-10 w-10 bg-gradient-to-br from-purple-500 to-blue-500">
                  <AvatarFallback className="bg-transparent text-white font-semibold">
                    {user?.name?.charAt(0) || "A"}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56 bg-slate-900 border-slate-700" align="end">
              <DropdownMenuLabel className="text-slate-200">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none">{user?.name}</p>
                  <p className="text-xs leading-none text-slate-400">{user?.email}</p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator className="bg-slate-700" />
              <DropdownMenuItem
                onClick={handleLogout}
                className="text-slate-300 hover:text-white hover:bg-slate-800 cursor-pointer"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Log out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  )
}
