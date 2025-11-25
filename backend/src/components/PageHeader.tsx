import { PageHeaderProps } from '@/types'

export default function PageHeader({ title, description, action }: PageHeaderProps) {
    return (
        <div className="mb-8 flex items-start justify-between">
            <div>
                <h1 className="text-4xl font-bold text-black mb-3">{title}</h1>
                <p className="text-zinc-500 text-lg">{description}</p>
            </div>
            {action && <div>{action}</div>}
        </div>
    )
}
