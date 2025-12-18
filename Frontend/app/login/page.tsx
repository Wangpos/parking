"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/contexts/auth-context"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Lock, Mail, ParkingCircle, AlertCircle, ArrowLeft } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Checkbox } from "@/components/ui/checkbox"

export default function LoginPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [rememberMe, setRememberMe] = useState(false)
  const [error, setError] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isMounted, setIsMounted] = useState(false)
  const { login, isAuthenticated, isLoading: authLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    setIsMounted(true)
  }, [])

  useEffect(() => {
    if (isMounted && isAuthenticated) {
      router.push("/admin")
    }
  }, [isAuthenticated, isMounted, router])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setIsLoading(true)

    const success = await login(email, password)

    if (success) {
      router.push("/admin")
    } else {
      setError("Invalid email or password")
      setIsLoading(false)
    }
  }

  // Don't show login form if already authenticated or still loading auth
  if (authLoading || (isMounted && isAuthenticated)) {
    return null
  }

  return (
    <div className="min-h-screen relative overflow-hidden bg-[#1a1625]">
      {/* Animated background particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {isMounted && [...Array(50)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-purple-400/30 rounded-full animate-twinkle"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
              animationDuration: `${2 + Math.random() * 3}s`,
            }}
          />
        ))}
      </div>

      {/* Gradient overlay for depth */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-900/20 via-transparent to-indigo-900/20 pointer-events-none"></div>

      {/* Back Button */}
      <button
        onClick={() => router.push("/")}
        className="absolute top-4 left-4 sm:top-6 sm:left-6 z-20 flex items-center gap-2 text-gray-300 hover:text-white transition-all duration-300 group"
      >
        <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg bg-purple-500/10 border border-purple-500/30 flex items-center justify-center group-hover:bg-purple-500/20 group-hover:border-purple-500/50 transition-all duration-300">
          <ArrowLeft className="w-4 h-4 sm:w-5 sm:h-5" />
        </div>
        <span className="text-xs sm:text-sm font-medium hidden sm:inline">Back to Home</span>
      </button>

      {/* Add keyframe animation styles */}
      <style jsx>{`
        @keyframes twinkle {
          0%, 100% { opacity: 0; transform: scale(0); }
          50% { opacity: 1; transform: scale(1); }
        }
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-20px); }
        }
        @keyframes slideInUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>

      {/* Content Container */}
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
        {/* Logo Section */}
        <div 
          className={`text-center mb-6 sm:mb-8 transition-all duration-700 ${
            isMounted ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-10'
          }`}
        >
          <div className="inline-flex items-center justify-center gap-3 mb-4 sm:mb-6">
            <div className="w-12 h-12 sm:w-16 sm:h-16 bg-gradient-to-br from-purple-500 to-purple-700 rounded-2xl flex items-center justify-center shadow-2xl shadow-purple-500/30 animate-float">
              <ParkingCircle className="w-8 h-8 sm:w-10 sm:h-10 text-white" />
            </div>
          </div>
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-2 sm:mb-4 tracking-tight">
            ParkHub
          </h1>
          <p className="text-sm sm:text-base md:text-lg text-gray-400">Real-time AI-powered parking system</p>
        </div>

        {/* Login Card */}
        <div 
          className={`w-full max-w-[480px] bg-[#252139] border border-purple-500/20 rounded-xl sm:rounded-2xl shadow-2xl shadow-purple-500/10 p-6 sm:p-8 transition-all duration-700 ${
            isMounted ? 'opacity-100 scale-100' : 'opacity-0 scale-90'
          }`}
          style={{ transitionDelay: '200ms' }}
        >
          <div className="mb-6 sm:mb-8 text-center">
            <h2 className="text-2xl sm:text-3xl font-bold text-white mb-2">Welcome Back</h2>
            <p className="text-gray-400 text-xs sm:text-sm">Sign in to access your dashboard</p>
          </div>

          {error && (
            <Alert 
              variant="destructive" 
              className="mb-4 sm:mb-6 bg-red-500/10 border-red-500/30 animate-in slide-in-from-top-2 duration-300"
            >
              <AlertCircle className="h-4 w-4 text-red-400 animate-pulse" />
              <AlertDescription className="text-red-400">{error}</AlertDescription>
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-5">
            <div 
              className={`space-y-2 transition-all duration-500 ${
                isMounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'
              }`}
              style={{ transitionDelay: '400ms' }}
            >
              <Label htmlFor="email" className="text-gray-300 text-sm font-medium">
                Email/Username*
              </Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 sm:h-5 sm:w-5 text-gray-500" />
                <Input
                  id="email"
                  type="email"
                  placeholder="admin@parking.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="pl-10 sm:pl-11 h-11 sm:h-12 bg-[#1a1625] border-purple-500/30 text-white placeholder:text-gray-500 focus:border-purple-500 focus:ring-purple-500/30 rounded-lg transition-all duration-300 hover:border-purple-500/50 text-sm sm:text-base"
                  required
                />
              </div>
            </div>

            <div 
              className={`space-y-2 transition-all duration-500 ${
                isMounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'
              }`}
              style={{ transitionDelay: '500ms' }}
            >
              <Label htmlFor="password" className="text-gray-300 text-sm font-medium">
                Password*
              </Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 sm:h-5 sm:w-5 text-gray-500" />
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pl-10 sm:pl-11 h-11 sm:h-12 bg-[#1a1625] border-purple-500/30 text-white placeholder:text-gray-500 focus:border-purple-500 focus:ring-purple-500/30 rounded-lg transition-all duration-300 hover:border-purple-500/50 text-sm sm:text-base"
                  required
                />
              </div>
            </div>

            <div 
              className={`flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-0 transition-all duration-500 ${
                isMounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'
              }`}
              style={{ transitionDelay: '600ms' }}
            >
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="remember" 
                  checked={rememberMe}
                  onCheckedChange={(checked) => setRememberMe(checked as boolean)}
                  className="border-purple-500/30 data-[state=checked]:bg-purple-600 data-[state=checked]:border-purple-600"
                />
                <label
                  htmlFor="remember"
                  className="text-sm text-gray-400 cursor-pointer select-none"
                >
                  Remember me
                </label>
              </div>
              <button
                type="button"
                className="text-sm text-purple-400 hover:text-purple-300 font-medium transition-colors"
              >
                Forgot password?
              </button>
            </div>

            <Button
              type="submit"
              className={`w-full bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white font-semibold h-11 sm:h-12 rounded-lg shadow-lg shadow-purple-500/30 hover:shadow-xl hover:shadow-purple-500/40 transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] text-sm sm:text-base ${
                isMounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'
              }`}
              style={{ transitionDelay: '700ms' }}
              disabled={isLoading}
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Signing in...
                </span>
              ) : (
                "Sign In"
              )}
            </Button>
          </form>

          {/* Demo credentials */}
          <div 
            className={`mt-5 sm:mt-6 p-3 sm:p-4 bg-purple-500/10 rounded-xl border border-purple-500/20 transition-all duration-500 ${
              isMounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'
            }`}
            style={{ transitionDelay: '800ms' }}
          >
            <p className="text-xs text-gray-400 mb-2 font-medium">🔑 Demo Credentials:</p>
            <p className="text-xs text-gray-300">Email: <span className="font-mono font-semibold text-purple-400 break-all">admin@parking.com</span></p>
            <p className="text-xs text-gray-300">Password: <span className="font-mono font-semibold text-purple-400">admin123</span></p>
          </div>
        </div>
      </div>
    </div>
  )
}