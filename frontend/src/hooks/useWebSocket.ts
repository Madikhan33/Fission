'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { WebSocketMessage } from '@/types'

interface UseWebSocketOptions {
    onMessage?: (message: WebSocketMessage) => void
    onConnect?: () => void
    onDisconnect?: () => void
    onError?: (error: Event) => void
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
    const [isConnected, setIsConnected] = useState(false)
    const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
    const wsRef = useRef<WebSocket | null>(null)
    const reconnectTimeoutRef = useRef<NodeJS.Timeout>()

    const connect = useCallback(() => {
        const token = localStorage.getItem('token')
        if (!token) {
            console.log('No token available for WebSocket connection')
            return
        }

        try {
            const ws = new WebSocket(`ws://localhost:8000/notifications/ws?token=${token}`)

            ws.onopen = () => {
                console.log('WebSocket connected')
                setIsConnected(true)
                options.onConnect?.()
            }

            ws.onmessage = (event) => {
                try {
                    const message: WebSocketMessage = JSON.parse(event.data)
                    setLastMessage(message)
                    options.onMessage?.(message)
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error)
                }
            }

            ws.onerror = (error) => {
                console.error('WebSocket error:', error)
                options.onError?.(error)
            }

            ws.onclose = () => {
                console.log('WebSocket disconnected')
                setIsConnected(false)
                options.onDisconnect?.()

                // Auto-reconnect after 3 seconds
                reconnectTimeoutRef.current = setTimeout(() => {
                    console.log('Attempting to reconnect WebSocket...')
                    connect()
                }, 3000)
            }

            wsRef.current = ws
        } catch (error) {
            console.error('Failed to create WebSocket connection:', error)
        }
    }, [options])

    const disconnect = useCallback(() => {
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current)
        }

        if (wsRef.current) {
            wsRef.current.close()
            wsRef.current = null
        }
    }, [])

    const sendMessage = useCallback((message: any) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(message))
        } else {
            console.warn('WebSocket is not connected')
        }
    }, [])

    const subscribeToAnalysis = useCallback((analysisId: number) => {
        sendMessage({
            action: 'subscribe_analysis',
            analysis_id: analysisId
        })
    }, [sendMessage])

    useEffect(() => {
        connect()

        return () => {
            disconnect()
        }
    }, [connect, disconnect])

    return {
        isConnected,
        lastMessage,
        sendMessage,
        subscribeToAnalysis,
        reconnect: connect,
        disconnect
    }
}
