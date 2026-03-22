import { cn } from "@/lib/utils"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export function LoginForm({ className, ...props }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Reset password flow
  const [step, setStep] = useState('login') // login | otp_request | otp_verify
  const [resetUsername, setResetUsername] = useState('')
  const [otp, setOtp] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')

  // ── Handle Login ──────────────────────────────────────────────
  const handleLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await fetch('/api/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })

      const data = await response.json()

      if (!response.ok) {
        setError(data.error || data.message || 'Invalid username or password')
        return
      }

      localStorage.setItem('refresh_token', data.data.refresh_token)
      localStorage.setItem('access_token', data.data.access_token)
      window.location.href = '/'

    } catch (err) {
      setError('Could not connect to server. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  // ── Handle OTP Request (Step 1) ───────────────────────────────
  const handleOtpRequest = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      const response = await fetch('/api/auth/reset_password/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: resetUsername }),
      })

      const data = await response.json()

      if (!response.ok) {
        setError(data.error || data.message || 'Could not send OTP')
        return
      }

      setSuccess(data.message || 'OTP sent to your email. Valid for 10 minutes.')
      setStep('otp_verify')

    } catch (err) {
      setError('Could not connect to server. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  //Handle Password Reset 
  const handlePasswordReset = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match')
      setLoading(false)
      return
    }

    try {
      const response = await fetch('/api/auth/reset_password/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: resetUsername,
          otp,
          new_password: newPassword,
          confirm_password: confirmPassword,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        setError(data.error || data.message || 'Could not reset password')
        return
      }

      setSuccess('Password reset successfully. You can now log in.')
      setStep('login')
      setResetUsername('')
      setOtp('')
      setNewPassword('')
      setConfirmPassword('')

    } catch (err) {
      setError('Could not connect to server. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  // ── Render ────────────────────────────────────────────────────
  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card className="bg-surface-card border border-surface-border">

        {/* Step 1 — Login */}
        {step === 'login' && (
          <>
            <CardHeader>
              <CardTitle className="text-2xl text-text-primary">Welcome Back</CardTitle>
              <CardDescription className="text-text-secondary">
                Enter your username and password to access the KPI system
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form className="flex flex-col gap-6" onSubmit={handleLogin}>

                {error && (
                  <div className="bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-3">
                    <p className="text-red-400 text-sm">{error}</p>
                  </div>
                )}

                {success && (
                  <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-lg px-4 py-3">
                    <p className="text-emerald-400 text-sm">{success}</p>
                  </div>
                )}

                <div className="flex flex-col gap-2">
                  <Label htmlFor="username" className="text-text-secondary">Username</Label>
                  <Input
                    id="username"
                    type="text"
                    placeholder="Enter your username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="bg-surface-muted border-surface-border text-text-primary placeholder:text-text-muted"
                  />
                </div>

                <div className="flex flex-col gap-2">
                  <div className="flex items-center">
                    <Label htmlFor="password" className="text-text-secondary">Password</Label>
                    <button
                      type="button"
                      onClick={() => { setStep('otp_request'); setError(''); setSuccess('') }}
                      className="ml-auto text-sm text-brand-400 hover:text-brand-300"
                    >
                      Forgot your password?
                    </button>
                  </div>
                  <Input
                    id="password"
                    type="password"
                    autocomplete ="new-password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="bg-surface-muted border-surface-border text-text-primary"
                  />
                </div>

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-brand-600 hover:bg-brand-700 text-white"
                >
                  {loading ? 'Logging in...' : 'Login'}
                </Button>

                <div className="text-center text-sm text-text-secondary">
                  Don't have an account?{" "}
                  <a href="#" className="text-brand-400 hover:text-brand-300 underline-offset-4 hover:underline">
                    Sign up
                  </a>
                </div>

              </form>
            </CardContent>
          </>
        )}

        {/* Step 2 — Enter Username to get OTP */}
        {step === 'otp_request' && (
          <>
            <CardHeader>
              <CardTitle className="text-2xl text-text-primary">Reset Password</CardTitle>
              <CardDescription className="text-text-secondary">
                Enter your username and we will send an OTP to your registered email
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form className="flex flex-col gap-6" onSubmit={handleOtpRequest}>

                {error && (
                  <div className="bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-3">
                    <p className="text-red-400 text-sm">{error}</p>
                  </div>
                )}

                <div className="flex flex-col gap-2">
                  <Label htmlFor="resetUsername" className="text-text-secondary">Username</Label>
                  <Input
                    id="resetUsername"
                    type="text"
                    placeholder="Enter your username"
                    value={resetUsername}
                    onChange={(e) => setResetUsername(e.target.value)}
                    className="bg-surface-muted border-surface-border text-text-primary placeholder:text-text-muted"
                  />
                </div>

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-brand-600 hover:bg-brand-700 text-white"
                >
                  {loading ? 'Sending OTP...' : 'Send OTP'}
                </Button>

                <button
                  type="button"
                  onClick={() => { setStep('login'); setError(''); setSuccess('') }}
                  className="text-center text-sm text-brand-400 hover:text-brand-300"
                >
                  Back to Login
                </button>

              </form>
            </CardContent>
          </>
        )}

        {/* Step 3 — Enter OTP + New Password */}
        {step === 'otp_verify' && (
          <>
            <CardHeader>
              <CardTitle className="text-2xl text-text-primary">Enter OTP</CardTitle>
              <CardDescription className="text-text-secondary">
                Enter the OTP sent to your email and your new password
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form className="flex flex-col gap-6" onSubmit={handlePasswordReset}>

                {error && (
                  <div className="bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-3">
                    <p className="text-red-400 text-sm">{error}</p>
                  </div>
                )}

                {success && (
                  <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-lg px-4 py-3">
                    <p className="text-emerald-400 text-sm">{success}</p>
                  </div>
                )}

                <div className="flex flex-col gap-2">
                  <Label htmlFor="otp" className="text-text-secondary">OTP Code</Label>
                  <Input
                    id="otp"
                    type="text"
                    placeholder="Enter OTP from your email"
                    value={otp}
                    onChange={(e) => setOtp(e.target.value)}
                    className="bg-surface-muted border-surface-border text-text-primary placeholder:text-text-muted"
                  />
                </div>

                <div className="flex flex-col gap-2">
                  <Label htmlFor="newPassword" className="text-text-secondary">New Password</Label>
                  <Input
                    id="newPassword"
                    type="password"
                    placeholder="Enter new password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="bg-surface-muted border-surface-border text-text-primary placeholder:text-text-muted"
                  />
                </div>

                <div className="flex flex-col gap-2">
                  <Label htmlFor="confirmPassword" className="text-text-secondary">Confirm Password</Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    placeholder="Confirm new password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="bg-surface-muted border-surface-border text-text-primary placeholder:text-text-muted"
                  />
                </div>

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-brand-600 hover:bg-brand-700 text-white"
                >
                  {loading ? 'Resetting...' : 'Reset Password'}
                </Button>

                <button
                  type="button"
                  onClick={() => { setStep('login'); setError(''); setSuccess('') }}
                  className="text-center text-sm text-brand-400 hover:text-brand-300"
                >
                  Back to Login
                </button>

              </form>
            </CardContent>
          </>
        )}

      </Card>
    </div>
  )
}