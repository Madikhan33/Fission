'use client'

import { useState } from 'react'
import PageHeader from '@/components/PageHeader'
import { User, Bell, Shield, Palette } from 'lucide-react'
import { SettingsTab } from '@/types'

export default function SettingsPage() {
    const [activeTab, setActiveTab] = useState<SettingsTab>('profile')

    const tabs: { id: SettingsTab; label: string; icon: React.ReactNode }[] = [
        { id: 'profile', label: 'Profile', icon: <User className="w-4 h-4" /> },
        { id: 'preferences', label: 'Preferences', icon: <Palette className="w-4 h-4" /> },
        { id: 'notifications', label: 'Notifications', icon: <Bell className="w-4 h-4" /> },
        { id: 'security', label: 'Security', icon: <Shield className="w-4 h-4" /> },
    ]

    return (
        <div className="p-8">
            <PageHeader
                title="Settings"
                description="Manage your account settings and preferences"
            />

            <div className="flex gap-8">
                {/* Sidebar Tabs */}
                <div className="w-64 flex-shrink-0">
                    <nav className="space-y-1">
                        {tabs.map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all ${activeTab === tab.id
                                        ? 'bg-black text-white'
                                        : 'text-zinc-700 hover:bg-zinc-100'
                                    }`}
                            >
                                {tab.icon}
                                {tab.label}
                            </button>
                        ))}
                    </nav>
                </div>

                {/* Content Area */}
                <div className="flex-1 bg-white border border-zinc-200 rounded-lg p-8">
                    {activeTab === 'profile' && <ProfileSettings />}
                    {activeTab === 'preferences' && <PreferencesSettings />}
                    {activeTab === 'notifications' && <NotificationSettings />}
                    {activeTab === 'security' && <SecuritySettings />}
                </div>
            </div>
        </div>
    )
}

function ProfileSettings() {
    return (
        <div className="space-y-6">
            <h2 className="text-2xl font-semibold text-black mb-6">Profile Settings</h2>

            <div className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-black mb-2">
                        Full Name
                    </label>
                    <input
                        type="text"
                        defaultValue="John Doe"
                        className="w-full px-4 py-2.5 border border-zinc-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent text-sm"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-black mb-2">
                        Email Address
                    </label>
                    <input
                        type="email"
                        defaultValue="john.doe@company.com"
                        className="w-full px-4 py-2.5 border border-zinc-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent text-sm"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-black mb-2">
                        Role
                    </label>
                    <input
                        type="text"
                        defaultValue="Frontend Developer"
                        className="w-full px-4 py-2.5 border border-zinc-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent text-sm"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-black mb-2">
                        Bio
                    </label>
                    <textarea
                        defaultValue="Passionate developer focused on creating beautiful user experiences."
                        rows={4}
                        className="w-full px-4 py-2.5 border border-zinc-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent resize-none text-sm"
                    />
                </div>
            </div>

            <button className="bg-black text-white px-6 py-2.5 rounded-lg font-medium hover:bg-zinc-800 transition-colors">
                Save Changes
            </button>
        </div>
    )
}

function PreferencesSettings() {
    return (
        <div className="space-y-6">
            <h2 className="text-2xl font-semibold text-black mb-6">Preferences</h2>

            <div className="space-y-4">
                <div className="flex items-center justify-between py-3 border-b border-zinc-100">
                    <div>
                        <div className="text-sm font-medium text-black">Theme</div>
                        <div className="text-xs text-zinc-500">Monochrome (Default)</div>
                    </div>
                    <div className="px-3 py-1 bg-zinc-100 rounded text-xs font-medium text-zinc-700">
                        Active
                    </div>
                </div>

                <div className="flex items-center justify-between py-3 border-b border-zinc-100">
                    <div>
                        <div className="text-sm font-medium text-black">Language</div>
                        <div className="text-xs text-zinc-500">English (US)</div>
                    </div>
                    <select className="px-3 py-1.5 border border-zinc-200 rounded text-xs">
                        <option>English (US)</option>
                        <option>English (UK)</option>
                        <option>Русский</option>
                    </select>
                </div>

                <div className="flex items-center justify-between py-3 border-b border-zinc-100">
                    <div>
                        <div className="text-sm font-medium text-black">Date Format</div>
                        <div className="text-xs text-zinc-500">MM/DD/YYYY</div>
                    </div>
                    <select className="px-3 py-1.5 border border-zinc-200 rounded text-xs">
                        <option>MM/DD/YYYY</option>
                        <option>DD/MM/YYYY</option>
                        <option>YYYY-MM-DD</option>
                    </select>
                </div>
            </div>
        </div>
    )
}

function NotificationSettings() {
    return (
        <div className="space-y-6">
            <h2 className="text-2xl font-semibold text-black mb-6">Notifications</h2>

            <div className="space-y-4">
                {[
                    { label: 'Email Notifications', description: 'Receive email updates about your tasks' },
                    { label: 'Task Assignments', description: 'Get notified when tasks are assigned to you' },
                    { label: 'Task Completions', description: 'Notifications when tasks are completed' },
                    { label: 'Team Updates', description: 'Updates about team member activities' },
                    { label: 'Weekly Summary', description: 'Receive weekly performance summaries' },
                ].map((item, index) => (
                    <div key={index} className="flex items-center justify-between py-3 border-b border-zinc-100">
                        <div>
                            <div className="text-sm font-medium text-black">{item.label}</div>
                            <div className="text-xs text-zinc-500">{item.description}</div>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" defaultChecked={index < 3} className="sr-only peer" />
                            <div className="w-11 h-6 bg-zinc-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-black rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-zinc-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-black"></div>
                        </label>
                    </div>
                ))}
            </div>
        </div>
    )
}

function SecuritySettings() {
    return (
        <div className="space-y-6">
            <h2 className="text-2xl font-semibold text-black mb-6">Security</h2>

            <div className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-black mb-2">
                        Current Password
                    </label>
                    <input
                        type="password"
                        placeholder="Enter current password"
                        className="w-full px-4 py-2.5 border border-zinc-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent text-sm"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-black mb-2">
                        New Password
                    </label>
                    <input
                        type="password"
                        placeholder="Enter new password"
                        className="w-full px-4 py-2.5 border border-zinc-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent text-sm"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-black mb-2">
                        Confirm New Password
                    </label>
                    <input
                        type="password"
                        placeholder="Confirm new password"
                        className="w-full px-4 py-2.5 border border-zinc-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent text-sm"
                    />
                </div>
            </div>

            <button className="bg-black text-white px-6 py-2.5 rounded-lg font-medium hover:bg-zinc-800 transition-colors">
                Update Password
            </button>

            <div className="pt-6 border-t border-zinc-200 mt-8">
                <h3 className="text-lg font-semibold text-black mb-4">Two-Factor Authentication</h3>
                <p className="text-sm text-zinc-600 mb-4">
                    Add an extra layer of security to your account
                </p>
                <button className="border border-zinc-200 text-black px-6 py-2.5 rounded-lg font-medium hover:bg-zinc-50 transition-colors">
                    Enable 2FA
                </button>
            </div>
        </div>
    )
}
