"use client"

import { useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { ArrowLeft, CreditCard, Wallet, Smartphone, CheckCircle2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Header } from "@/components/header"
import { PaymentForm } from "@/components/payment-form"

export default function PaymentPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  
  // Get parameters from URL
  const slotId = searchParams.get("slot") || "A1-001"
  const duration = searchParams.get("duration") || "2h 30m"
  const fee = searchParams.get("fee") || "50"
  const vehicleNumber = searchParams.get("vehicle") || "BP-2024-XXX"
  const area = searchParams.get("area") || "Main Entrance - North"

  const [paymentComplete, setPaymentComplete] = useState(false)
  const [selectedMethod, setSelectedMethod] = useState<string>("")

  const handlePaymentSuccess = (method: string) => {
    setSelectedMethod(method)
    setPaymentComplete(true)
  }

  const handleBackToDashboard = () => {
    router.push("/")
  }

  if (paymentComplete) {
    return (
      <>
        <Header />
        <div className="flex-1 container mx-auto px-4 py-8">
          <div className="max-w-2xl mx-auto">
            <Card className="border-green-500 border-2">
              <CardHeader className="text-center">
                <div className="mx-auto mb-4 w-16 h-16 bg-green-500 rounded-full flex items-center justify-center">
                  <CheckCircle2 className="w-10 h-10 text-white" />
                </div>
                <CardTitle className="text-2xl text-green-600">Payment Successful!</CardTitle>
                <CardDescription>Your parking fee has been paid</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="bg-muted rounded-lg p-4 space-y-3">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Transaction ID:</span>
                    <span className="font-mono font-semibold">TXN-{Date.now().toString().slice(-8)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Payment Method:</span>
                    <span className="font-semibold capitalize">{selectedMethod}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Slot ID:</span>
                    <span className="font-semibold">{slotId}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Vehicle:</span>
                    <span className="font-semibold">{vehicleNumber}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Parking Area:</span>
                    <span className="font-semibold">{area}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Duration:</span>
                    <span className="font-semibold">{duration}</span>
                  </div>
                  <div className="border-t pt-3 flex justify-between text-lg">
                    <span className="font-semibold">Amount Paid:</span>
                    <span className="font-bold text-green-600">Nu. {fee}</span>
                  </div>
                </div>
                
                <div className="text-sm text-muted-foreground text-center">
                  Payment processed on {new Date().toLocaleString()}
                </div>

                <Button onClick={handleBackToDashboard} className="w-full" size="lg">
                  Back to Dashboard
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </>
    )
  }

  return (
    <>
      <Header />
      <div className="flex-1 container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <Button
            variant="ghost"
            onClick={() => router.back()}
            className="mb-6"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Payment Summary */}
            <div className="lg:col-span-1">
              <Card>
                <CardHeader>
                  <CardTitle>Payment Summary</CardTitle>
                  <CardDescription>Parking fee details</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Slot:</span>
                      <span className="font-semibold">{slotId}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Vehicle:</span>
                      <span className="font-semibold">{vehicleNumber}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Area:</span>
                      <span className="font-semibold text-right max-w-[180px]">{area}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Duration:</span>
                      <span className="font-semibold">{duration}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Rate:</span>
                      <span className="font-semibold">Nu. 20/hour</span>
                    </div>
                  </div>

                  <div className="border-t pt-4">
                    <div className="flex justify-between items-center">
                      <span className="font-semibold">Total Amount:</span>
                      <span className="text-2xl font-bold text-primary">Nu. {fee}</span>
                    </div>
                  </div>

                  <div className="bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg p-3 text-sm">
                    <p className="text-blue-800 dark:text-blue-200">
                      <strong>Note:</strong> Payment is required before vehicle exit. Keep your transaction ID for reference.
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Payment Form */}
            <div className="lg:col-span-2">
              <PaymentForm
                amount={fee}
                slotId={slotId}
                vehicleNumber={vehicleNumber}
                onPaymentSuccess={handlePaymentSuccess}
              />
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
