"use client"

interface MiniChartProps {
  data: number[]
  type?: "line" | "bar" | "area"
  color?: string
  height?: number
  className?: string
}

export function MiniChart({ data, type = "line", color = "#FFD700", height = 40, className = "" }: MiniChartProps) {
  const max = Math.max(...data)
  const min = Math.min(...data)
  const range = max - min || 1

  const points = data
    .map((value, index) => {
      const x = (index / (data.length - 1)) * 100
      const y = ((max - value) / range) * 100
      return `${x},${y}`
    })
    .join(" ")

  if (type === "bar") {
    return (
      <div className={`flex items-end justify-between h-${height} ${className}`} style={{ height: `${height}px` }}>
        {data.map((value, index) => {
          const barHeight = ((value - min) / range) * height
          return (
            <div
              key={index}
              className="w-1 rounded-t"
              style={{
                height: `${barHeight}px`,
                backgroundColor: color,
                opacity: 0.8,
              }}
            />
          )
        })}
      </div>
    )
  }

  return (
    <svg className={className} width="100%" height={height} viewBox="0 0 100 100" preserveAspectRatio="none">
      {type === "area" && <polygon points={`0,100 ${points} 100,100`} fill={color} fillOpacity="0.2" />}
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}
