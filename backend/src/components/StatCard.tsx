import { StatCardProps } from '@/types'

export default function StatCard({ title, value, icon, trend }: StatCardProps) {
    return (
        <div className="bg-white border border-zinc-200 rounded-lg p-6 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-4">
                <div className="p-2 bg-zinc-100 rounded-lg">
                    {icon}
                </div>
                {trend && (
                    <span className={`text-xs font-medium ${trend.isPositive ? 'text-zinc-700' : 'text-zinc-500'}`}>
                        {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
                    </span>
                )}
            </div>
            <div className="text-3xl font-bold text-black mb-1">{value}</div>
            <div className="text-sm text-zinc-600">{title}</div>
        </div>
    )
}
