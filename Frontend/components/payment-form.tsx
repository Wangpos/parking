"use client"

import { useState } from "react"
import { CreditCard, Smartphone, Wallet, Building2, CheckCircle2, AlertCircle } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { OTPDialog } from "@/components/otp-dialog"

interface PaymentFormProps {
  amount: string
  slotId: string
  vehicleNumber: string
  onPaymentSuccess: (method: string) => void
}

type PaymentMethod = "card" | "mobile" | "wallet" | "bank"

export function PaymentForm({ amount, slotId, vehicleNumber, onPaymentSuccess }: PaymentFormProps) {
  const [selectedMethod, setSelectedMethod] = useState<PaymentMethod>("card")
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string>("")
  const [showOTP, setShowOTP] = useState(false)
  const [otpPhoneNumber, setOtpPhoneNumber] = useState("")

  // Card payment state
  const [cardNumber, setCardNumber] = useState("")
  const [cardName, setCardName] = useState("")
  const [expiryDate, setExpiryDate] = useState("")
  const [cvv, setCvv] = useState("")

  // Mobile payment state
  const [mobileNumber, setMobileNumber] = useState("")
  const [mobileProvider, setMobileProvider] = useState("bmobile")

  // Wallet state
  const [walletType, setWalletType] = useState("paytm")
  const [walletPhone, setWalletPhone] = useState("")

  // Bank transfer state
  const [accountNumber, setAccountNumber] = useState("")
  const [bankName, setBankName] = useState("bob")

  const formatCardNumber = (value: string) => {
    const cleaned = value.replace(/\s/g, "")
    const formatted = cleaned.match(/.{1,4}/g)?.join(" ") || cleaned
    return formatted.slice(0, 19) // 16 digits + 3 spaces
  }

  const formatExpiryDate = (value: string) => {
    const cleaned = value.replace(/\D/g, "")
    if (cleaned.length >= 2) {
      return cleaned.slice(0, 2) + "/" + cleaned.slice(2, 4)
    }
    return cleaned
  }

  const handlePayment = async () => {
    setError("")

    // Validation
    if (selectedMethod === "card") {
      if (!cardNumber || cardNumber.replace(/\s/g, "").length !== 16) {
        setError("Please enter a valid 16-digit card number")
        return
      }
      if (!cardName || cardName.trim().length < 3) {
        setError("Please enter the cardholder name")
        return
      }
      if (!expiryDate || expiryDate.length !== 5) {
        setError("Please enter a valid expiry date (MM/YY)")
        return
      }
      if (!cvv || cvv.length < 3) {
        setError("Please enter a valid CVV")
        return
      }
      
      // Card payments process directly without OTP
      setIsProcessing(true)
      setTimeout(() => {
        setIsProcessing(false)
        onPaymentSuccess(selectedMethod)
      }, 2000)
    } else if (selectedMethod === "mobile") {
      if (!mobileNumber || mobileNumber.length < 8) {
        setError("Please enter a valid mobile number")
        return
      }
      // Show OTP dialog for mobile payment
      setOtpPhoneNumber(mobileNumber)
      setShowOTP(true)
    } else if (selectedMethod === "wallet") {
      if (!walletPhone || walletPhone.length < 8) {
        setError("Please enter a valid phone number")
        return
      }
      // Show OTP dialog for wallet payment
      setOtpPhoneNumber(walletPhone)
      setShowOTP(true)
    } else if (selectedMethod === "bank") {
      if (!accountNumber || accountNumber.length < 10) {
        setError("Please enter a valid account number")
        return
      }
      // Show OTP dialog for bank transfer
      setOtpPhoneNumber("77XXXXXX") // Masked registered phone
      setShowOTP(true)
    }
  }

  const handleOTPVerified = () => {
    setShowOTP(false)
    setIsProcessing(true)
    // Simulate final processing
    setTimeout(() => {
      setIsProcessing(false)
      onPaymentSuccess(selectedMethod)
    }, 1000)
  }

  const paymentMethods = [
    {
      id: "card" as PaymentMethod,
      name: "Credit/Debit Card",
      icon: CreditCard,
      description: "Pay with Visa, Mastercard, or RuPay",
    },
    {
      id: "mobile" as PaymentMethod,
      name: "Mobile Banking",
      icon: Smartphone,
      description: "BMobile Pay, TashiCell Pay",
    },
    {
      id: "wallet" as PaymentMethod,
      name: "Digital Wallet",
      icon: Wallet,
      description: "PayTM, PhonePe, Google Pay",
    },
    {
      id: "bank" as PaymentMethod,
      name: "Bank Transfer",
      icon: Building2,
      description: "Direct bank transfer",
    },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle>Select Payment Method</CardTitle>
        <CardDescription>Choose how you'd like to pay for parking</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Payment Method Selection */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {paymentMethods.map((method) => (
            <button
              key={method.id}
              type="button"
              onClick={() => setSelectedMethod(method.id)}
              className={`p-4 rounded-lg border-2 text-left transition-all hover:border-primary ${
                selectedMethod === method.id
                  ? "border-primary bg-primary/5"
                  : "border-border"
              }`}
            >
              <div className="flex items-start gap-3">
                <method.icon
                  className={`w-5 h-5 mt-0.5 ${
                    selectedMethod === method.id ? "text-primary" : "text-muted-foreground"
                  }`}
                />
                <div className="flex-1">
                  <div className="font-semibold text-sm">{method.name}</div>
                  <div className="text-xs text-muted-foreground mt-1">{method.description}</div>
                </div>
                {selectedMethod === method.id && (
                  <CheckCircle2 className="w-5 h-5 text-primary flex-shrink-0" />
                )}
              </div>
            </button>
          ))}
        </div>

        {/* Payment Details Forms */}
        <div className="mt-6">
          {selectedMethod === "card" && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="cardNumber">Card Number</Label>
                <Input
                  id="cardNumber"
                  placeholder="1234 5678 9012 3456"
                  value={cardNumber}
                  onChange={(e) => setCardNumber(formatCardNumber(e.target.value))}
                  maxLength={19}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="cardName">Cardholder Name</Label>
                <Input
                  id="cardName"
                  placeholder="John Doe"
                  value={cardName}
                  onChange={(e) => setCardName(e.target.value)}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="expiry">Expiry Date</Label>
                  <Input
                    id="expiry"
                    placeholder="MM/YY"
                    value={expiryDate}
                    onChange={(e) => setExpiryDate(formatExpiryDate(e.target.value))}
                    maxLength={5}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="cvv">CVV</Label>
                  <Input
                    id="cvv"
                    type="password"
                    placeholder="123"
                    value={cvv}
                    onChange={(e) => setCvv(e.target.value.replace(/\D/g, "").slice(0, 4))}
                    maxLength={4}
                  />
                </div>
              </div>
              <div className="flex gap-2 mt-4">
                <Badge variant="secondary">🔒 Secure Payment</Badge>
                <Badge variant="secondary">Visa</Badge>
                <Badge variant="secondary">Mastercard</Badge>
                <Badge variant="secondary">RuPay</Badge>
              </div>
            </div>
          )}

          {selectedMethod === "mobile" && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Select Provider</Label>
                <RadioGroup value={mobileProvider} onValueChange={setMobileProvider}>
                  <div className="flex items-center space-x-2 border rounded-lg p-3">
                    <RadioGroupItem value="bmobile" id="bmobile" />
                    <Label htmlFor="bmobile" className="flex-1 cursor-pointer">
                      <div className="font-semibold">BMobile Pay</div>
                      <div className="text-xs text-muted-foreground">Bhutan Telecom Mobile Banking</div>
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2 border rounded-lg p-3">
                    <RadioGroupItem value="tashicell" id="tashicell" />
                    <Label htmlFor="tashicell" className="flex-1 cursor-pointer">
                      <div className="font-semibold">TashiCell Pay</div>
                      <div className="text-xs text-muted-foreground">TashiCell Mobile Banking</div>
                    </Label>
                  </div>
                </RadioGroup>
              </div>
              <div className="space-y-2">
                <Label htmlFor="mobileNumber">Mobile Number</Label>
                <Input
                  id="mobileNumber"
                  placeholder="17XXXXXX"
                  value={mobileNumber}
                  onChange={(e) => setMobileNumber(e.target.value.replace(/\D/g, "").slice(0, 8))}
                />
              </div>
              <Alert>
                <Smartphone className="h-4 w-4" />
                <AlertDescription>
                  You will receive an OTP on your registered mobile number to confirm the payment.
                </AlertDescription>
              </Alert>
            </div>
          )}

          {selectedMethod === "wallet" && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Select Wallet</Label>
                <RadioGroup value={walletType} onValueChange={setWalletType}>
                  <div className="flex items-center space-x-2 border rounded-lg p-3">
                    <RadioGroupItem value="paytm" id="paytm" />
                    <Label htmlFor="paytm" className="flex-1 cursor-pointer font-semibold">
                      PayTM Wallet
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2 border rounded-lg p-3">
                    <RadioGroupItem value="phonepe" id="phonepe" />
                    <Label htmlFor="phonepe" className="flex-1 cursor-pointer font-semibold">
                      PhonePe
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2 border rounded-lg p-3">
                    <RadioGroupItem value="googlepay" id="googlepay" />
                    <Label htmlFor="googlepay" className="flex-1 cursor-pointer font-semibold">
                      Google Pay
                    </Label>
                  </div>
                </RadioGroup>
              </div>
              <div className="space-y-2">
                <Label htmlFor="walletPhone">Registered Phone Number</Label>
                <Input
                  id="walletPhone"
                  placeholder="17XXXXXX"
                  value={walletPhone}
                  onChange={(e) => setWalletPhone(e.target.value.replace(/\D/g, "").slice(0, 8))}
                />
              </div>
            </div>
          )}

          {selectedMethod === "bank" && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Select Bank</Label>
                <RadioGroup value={bankName} onValueChange={setBankName}>
                  <div className="flex items-center space-x-2 border rounded-lg p-3">
                    <RadioGroupItem value="bob" id="bob" />
                    <Label htmlFor="bob" className="flex-1 cursor-pointer">
                      <div className="font-semibold">Bank of Bhutan (BoB)</div>
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2 border rounded-lg p-3">
                    <RadioGroupItem value="bnb" id="bnb" />
                    <Label htmlFor="bnb" className="flex-1 cursor-pointer">
                      <div className="font-semibold">Bhutan National Bank (BNB)</div>
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2 border rounded-lg p-3">
                    <RadioGroupItem value="dpnb" id="dpnb" />
                    <Label htmlFor="dpnb" className="flex-1 cursor-pointer">
                      <div className="font-semibold">Druk PNB Bank</div>
                    </Label>
                  </div>
                </RadioGroup>
              </div>
              <div className="space-y-2">
                <Label htmlFor="accountNumber">Account Number</Label>
                <Input
                  id="accountNumber"
                  placeholder="Enter your account number"
                  value={accountNumber}
                  onChange={(e) => setAccountNumber(e.target.value.replace(/\D/g, "").slice(0, 16))}
                />
              </div>
              <Alert>
                <Building2 className="h-4 w-4" />
                <AlertDescription>
                  The amount will be debited directly from your bank account.
                </AlertDescription>
              </Alert>
            </div>
          )}
        </div>

        {/* Payment Button */}
        <div className="pt-4 border-t">
          <Button
            onClick={handlePayment}
            disabled={isProcessing}
            className="w-full"
            size="lg"
          >
            {isProcessing ? (
              <>
                <div className="animate-spin mr-2 h-4 w-4 border-2 border-current border-t-transparent rounded-full" />
                Processing Payment...
              </>
            ) : (
              <>
                Pay Nu. {amount}
              </>
            )}
          </Button>
          <p className="text-xs text-muted-foreground text-center mt-3">
            Your payment information is secured with 256-bit SSL encryption
          </p>
        </div>
      </CardContent>

      {/* OTP Verification Dialog */}
      <OTPDialog
        open={showOTP}
        onOpenChange={setShowOTP}
        phoneNumber={otpPhoneNumber}
        paymentMethod={selectedMethod}
        onVerifySuccess={handleOTPVerified}
      />
    </Card>
  )
}
