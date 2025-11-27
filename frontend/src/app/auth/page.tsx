'use client'

import { useState } from 'react'
import { Lock, Mail, Eye, EyeOff, User as UserIcon } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useApp } from '@/contexts/AppContext'
import { authApi } from '@/services/api'

export default function AuthPage() {
    const [isLogin, setIsLogin] = useState(true)
    const [showPassword, setShowPassword] = useState(false)
    const [username, setUsername] = useState('')
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [isLoading, setIsLoading] = useState(false)

    const { login } = useApp()
    const router = useRouter()

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')
        setIsLoading(true)

        try {
            if (isLogin) {
                // Login
                const data = await authApi.login(username, password)
                console.log('Login response:', data)
                // Save token first
                localStorage.setItem('token', data.access_token)
                // Then get user data
                const userData = await authApi.getMe()
                console.log('User data:', userData)
                login(data.access_token, userData)
                router.push('/dashboard')
            } else {
                // Register
                await authApi.register(username, email, password)
                // Auto login after registration
                const data = await authApi.login(username, password)
                console.log('Login after register:', data)
                // Save token first
                localStorage.setItem('token', data.access_token)
                // Then get user data
                const userData = await authApi.getMe()
                console.log('User data:', userData)
                login(data.access_token, userData)
                router.push('/dashboard')
            }
        } catch (err: any) {
            console.error('Auth error:', err)
            let errorMessage = 'Authentication failed'

            if (err.response?.data?.detail) {
                if (typeof err.response.data.detail === 'string') {
                    errorMessage = err.response.data.detail
                } else if (Array.isArray(err.response.data.detail)) {
                    errorMessage = err.response.data.detail.map((e: any) => e.msg).join(', ')
                }
            } else if (err.message) {
                errorMessage = err.message
            }

            setError(errorMessage)
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-white flex items-center justify-center p-4">
            <div className="w-full max-w-md">
                {/* Logo/Title */}
                <div className="text-center mb-8">
                    <div className="w-16 h-16 bg-black rounded-full flex items-center justify-center mx-auto mb-4">
                        <Lock className="w-8 h-8 text-white" />
                    </div>
                    <h1 className="text-3xl font-bold text-black mb-2">AI Task Manager</h1>
                    <p className="text-zinc-500">
                        {isLogin ? 'Sign in to your account' : 'Create a new account'}
                    </p>
                </div>

                {/* Auth Form */}
                <div className="bg-white border border-zinc-200 rounded-lg p-8 shadow-sm">
                    <form onSubmit={handleSubmit} className="space-y-6">
                        {/* Username Input */}
                        <div>
                            <label htmlFor="username" className="block text-sm font-medium text-black mb-2">
                                Username
                            </label>
                            <div className="relative">
                                <UserIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-400" />
                                <input
                                    id="username"
                                    type="text"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    placeholder="your_username"
                                    required
                                    className="w-full pl-12 pr-4 py-3 border border-zinc-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent text-sm"
                                />
                            </div>
                        </div>

                        {/* Email Input (only for registration) */}
                        {!isLogin && (
                            <div>
                                <label htmlFor="email" className="block text-sm font-medium text-black mb-2">
                                    Email Address
                                </label>
                                <div className="relative">
                                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-400" />
                                    <input
                                        id="email"
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        placeholder="you@company.com"
                                        required
                                        className="w-full pl-12 pr-4 py-3 border border-zinc-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent text-sm"
                                    />
                                </div>
                            </div>
                        )}

                        {/* Password Input */}
                        <div>
                            <label htmlFor="password" className="block text-sm font-medium text-black mb-2">
                                Password
                            </label>
                            <div className="relative">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-400" />
                                <input
                                    id="password"
                                    type={showPassword ? 'text' : 'password'}
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="••••••••"
                                    required
                                    className="w-full pl-12 pr-12 py-3 border border-zinc-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent text-sm"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-4 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-zinc-600 transition-colors"
                                >
                                    {showPassword ? (
                                        <EyeOff className="w-5 h-5" />
                                    ) : (
                                        <Eye className="w-5 h-5" />
                                    )}
                                </button>
                            </div>
                        </div>

                        {/* Error Message */}
                        {error && (
                            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                                {error}
                            </div>
                        )}

                        {/* Submit Button */}
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full bg-black text-white py-3 rounded-lg font-medium hover:bg-zinc-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isLoading ? 'Loading...' : (isLogin ? 'Sign In' : 'Sign Up')}
                        </button>
                    </form>

                    {/* Toggle Login/Register */}
                    <div className="mt-6 text-center text-sm text-zinc-600">
                        {isLogin ? "Don't have an account? " : "Already have an account? "}
                        <button
                            onClick={() => {
                                setIsLogin(!isLogin)
                                setError('')
                            }}
                            className="text-black font-medium hover:text-zinc-700"
                        >
                            {isLogin ? 'Sign up' : 'Sign in'}
                        </button>
                    </div>
                </div>

                {/* Footer */}
                <div className="mt-8 text-center text-xs text-zinc-400">
                    <p>© 2024 AI Task Manager. All rights reserved.</p>
                </div>
            </div>
        </div>
    )
}
