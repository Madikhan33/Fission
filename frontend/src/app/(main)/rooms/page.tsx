'use client'

import { useState, useEffect } from 'react'
import { Plus, Users, ArrowRight } from 'lucide-react'
import { useRouter } from 'next/navigation'
import PageHeader from '@/components/PageHeader'
import CreateRoomModal from '@/components/CreateRoomModal'
import { roomsApi } from '@/services/api'
import { Room } from '@/types'

export default function RoomsPage() {
    const router = useRouter()
    const [rooms, setRooms] = useState<Room[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)

    const fetchRooms = async () => {
        try {
            const data = await roomsApi.getAll()
            setRooms(data)
        } catch (error) {
            console.error('Failed to fetch rooms:', error)
        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        fetchRooms()
    }, [])

    return (
        <div className="space-y-6">
            <PageHeader
                title="Rooms"
                description="Manage your team workspaces and collaboration channels"
                action={
                    <button
                        onClick={() => setIsCreateModalOpen(true)}
                        className="flex items-center gap-2 px-4 py-2 bg-black text-white rounded-lg text-sm font-medium hover:bg-zinc-800 transition-colors"
                    >
                        <Plus className="w-4 h-4" />
                        Create Room
                    </button>
                }
            />

            {isLoading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="h-48 bg-zinc-100 rounded-xl animate-pulse" />
                    ))}
                </div>
            ) : rooms.length === 0 ? (
                <div className="text-center py-12 bg-zinc-50 rounded-xl border border-zinc-100">
                    <div className="w-12 h-12 bg-zinc-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Users className="w-6 h-6 text-zinc-400" />
                    </div>
                    <h3 className="text-lg font-medium text-black mb-2">No rooms found</h3>
                    <p className="text-zinc-500 mb-6">Create a room to start collaborating with your team</p>
                    <button
                        onClick={() => setIsCreateModalOpen(true)}
                        className="text-sm font-medium text-black hover:underline"
                    >
                        Create your first room
                    </button>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {rooms.map((room) => (
                        <div
                            key={room.id}
                            onClick={() => router.push(`/rooms/${room.id}`)}
                            className="group bg-white p-6 rounded-xl border border-zinc-200 hover:border-black/20 hover:shadow-lg transition-all cursor-pointer"
                        >
                            <div className="flex justify-between items-start mb-4">
                                <div className="p-2 bg-zinc-50 rounded-lg group-hover:bg-black/5 transition-colors">
                                    <Users className="w-5 h-5 text-black" />
                                </div>
                                <span className="text-xs font-medium text-zinc-500 bg-zinc-100 px-2 py-1 rounded-full">
                                    {room.members?.length || 0} members
                                </span>
                            </div>

                            <h3 className="text-lg font-semibold text-black mb-2 group-hover:text-blue-600 transition-colors">
                                {room.name}
                            </h3>

                            <p className="text-sm text-zinc-500 line-clamp-2 mb-4 h-10">
                                {room.description || 'No description provided'}
                            </p>

                            <div className="flex items-center text-sm font-medium text-black group-hover:translate-x-1 transition-transform">
                                View Details
                                <ArrowRight className="w-4 h-4 ml-1" />
                            </div>
                        </div>
                    ))}
                </div>
            )}

            <CreateRoomModal
                isOpen={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)}
                onRoomCreated={fetchRooms}
            />
        </div>
    )
}
