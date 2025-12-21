"use client"

import { useState, useEffect, useRef } from "react"
import { Shield, RefreshCw, CheckCircle2, AlertCircle } from "lucide-react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Alert, AlertDescription } from "@/components/ui/alert"

interface OTPDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  phoneNumber: string
  paymentMethod: string
  onVerifySuccess: () => void
}

export function OTPDialog({ open, onOpenChange, phoneNumber, paymentMethod, onVerifySuccess }: OTPDialogProps) {
  const [otp, setOtp] = useState(["", "", "", "", "", ""])
  const [isVerifying, setIsVerifying] = useState(false)
  const [error, setError] = useState("")
  const [timeLeft, setTimeLeft] = useState(120) // 2 minutes
  const [canResend, setCanResend] = useState(false)
  const [generatedOTP, setGeneratedOTP] = useState("")
  const inputRefs = useRef<(HTMLInputElement | null)[]>([])

  // Generate OTP when dialog opens
  useEffect(() => {
    if (open) {
      const newOTP = Math.floor(100000 + Math.random() * 900000).toString()
      setGeneratedOTP(newOTP)
      setTimeLeft(120)
      setCanResend(false)
      setOtp(["", "", "", "", "", ""])
      setError("")
      
      // Simulate sending OTP
      console.log(`OTP sent to ${phoneNumber}: ${newOTP}`)
      
      // For demo purposes, show OTP in alert
      setTimeout(() => {
        alert(`Demo Mode: Your OTP is ${newOTP}`)
      }, 500)
    }
  }, [open, phoneNumber])

  // Timer countdown
  useEffect(() => {
    if (open && timeLeft > 0) {
      const timer = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            setCanResend(true)
            return 0
          }
          return prev - 1
        })
      }, 1000)

      return () => clearInterval(timer)
    }
  }, [open, timeLeft])

  const handleOTPChange = (index: number, value: string) => {
    if (!/^\d*$/.test(value)) return

    const newOTP = [...otp]
    newOTP[index] = value.slice(-1)
    setOtp(newOTP)
    setError("")

    // Auto-focus next input
    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus()
    }
  }

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Backspace" && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus()
    }
  }

  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault()
    const pastedData = e.clipboardData.getData("text").slice(0, 6)
    if (!/^\d+$/.test(pastedData)) return

    const newOTP = pastedData.split("").concat(Array(6).fill("")).slice(0, 6)
    setOtp(newOTP)
    
    // Focus last filled input or next empty
    const nextIndex = Math.min(pastedData.length, 5)
    inputRefs.current[nextIndex]?.focus()
  }

  const handleVerify = () => {
    const enteredOTP = otp.join("")
    
    if (enteredOTP.length !== 6) {
      setError("Please enter complete OTP")
      return
    }

    setIsVerifying(true)

    // Simulate verification delay
    setTimeout(() => {
      if (enteredOTP === generatedOTP) {
        setIsVerifying(false)
        onVerifySuccess()
      } else {
        setIsVerifying(false)
        setError("Invalid OTP. Please try again.")
        setOtp(["", "", "", "", "", ""])
        inputRefs.current[0]?.focus()
      }
    }, 1500)
  }

  const handleResend = () => {
    const newOTP = Math.floor(100000 + Math.random() * 900000).toString()
    setGeneratedOTP(newOTP)
    setTimeLeft(120)
    setCanResend(false)
    setOtp(["", "", "", "", "", ""])
    setError("")
    
    console.log(`OTP resent to ${phoneNumber}: ${newOTP}`)
    alert(`Demo Mode: Your new OTP is ${newOTP}`)
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, "0")}`
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="mx-auto mb-4 w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <DialogTitle className="text-center text-xl">Enter Verification Code</DialogTitle>
          <DialogDescription className="text-center">
            We've sent a 6-digit OTP to<br />
            <span className="font-semibold text-foreground">{phoneNumber}</span>
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* OTP Input */}
          <div className="flex justify-center gap-2">
            {otp.map((digit, index) => (
              <Input
                key={index}
                ref={(el) => {
                  inputRefs.current[index] = el
                }}
                type="text"
                inputMode="numeric"
                maxLength={1}
                value={digit}
                onChange={(e) => handleOTPChange(index, e.target.value)}
                onKeyDown={(e) => handleKeyDown(index, e)}
                onPaste={handlePaste}
                className="w-12 h-12 text-center text-lg font-bold"
                disabled={isVerifying}
              />
            ))}
          </div>

          {/* Timer */}
          <div className="text-center">
            {timeLeft > 0 ? (
              <p className="text-sm text-muted-foreground">
                Time remaining:{" "}
                <span className="font-semibold text-foreground">{formatTime(timeLeft)}</span>
              </p>
            ) : (
              <p className="text-sm text-red-500 font-semibold">OTP expired</p>
            )}
          </div>

          {/* Verify Button */}
          <Button
            onClick={handleVerify}
            disabled={otp.join("").length !== 6 || isVerifying || timeLeft === 0}
            className="w-full"
            size="lg"
          >
            {isVerifying ? (
              <>
                <div className="animate-spin mr-2 h-4 w-4 border-2 border-current border-t-transparent rounded-full" />
                Verifying...
              </>
            ) : (
              <>
                <CheckCircle2 className="mr-2 h-4 w-4" />
                Verify & Pay
              </>
            )}
          </Button>

          {/* Resend OTP */}
          <div className="text-center">
            <Button
              variant="link"
              onClick={handleResend}
              disabled={!canResend}
              className="text-sm"
            >
              <RefreshCw className={`mr-2 h-3 w-3 ${!canResend ? "opacity-50" : ""}`} />
              {canResend ? "Resend OTP" : "Resend OTP"}
            </Button>
          </div>

          <Alert>
            <Shield className="h-4 w-4" />
            <AlertDescription className="text-xs">
              Never share your OTP with anyone. Our team will never ask for your OTP.
            </AlertDescription>
          </Alert>
        </div>
      </DialogContent>
    </Dialog>
  )
}
