"use client"

import { useEffect, useState } from "react"

interface ParkingDurationTimerProps {
  entryTime: string // Format: "10:45 AM"
  className?: string
}

export function ParkingDurationTimer({ entryTime, className = "" }: ParkingDurationTimerProps) {
  const [duration, setDuration] = useState("")

  useEffect(() => {
    const calculateDuration = () => {
      // Parse entry time
      const [time, period] = entryTime.split(" ")
      const [entryHours, entryMinutes] = time.split(":").map(Number)
      
      // Convert to 24-hour format
      let hour24 = entryHours
      if (period === "PM" && entryHours !== 12) {
        hour24 = entryHours + 12
      } else if (period === "AM" && entryHours === 12) {
        hour24 = 0
      }

      // Create entry date (today with entry time)
      const now = new Date()
      const entry = new Date(now)
      entry.setHours(hour24, entryMinutes, 0, 0)

      // If entry time is in the future, assume it was yesterday
      if (entry > now) {
        entry.setDate(entry.getDate() - 1)
      }

      // Calculate difference in milliseconds
      const diffMs = now.getTime() - entry.getTime()
      
      // Convert to hours and minutes
      const totalMinutes = Math.floor(diffMs / (1000 * 60))
      const durationHours = Math.floor(totalMinutes / 60)
      const durationMins = totalMinutes % 60

      // Format duration
      if (durationHours > 0) {
        setDuration(`${durationHours}h ${durationMins}m`)
      } else {
        setDuration(`${durationMins}m`)
      }
    }

    // Calculate immediately
    calculateDuration()

    // Update every minute
    const interval = setInterval(calculateDuration, 60000)

    return () => clearInterval(interval)
  }, [entryTime])

  return <span className={className}>{duration}</span>
}
