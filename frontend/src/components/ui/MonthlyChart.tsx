const MONTHS = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

const W = 360
const BAR_AREA_H = 110
const LABEL_H = 18
const TOP_PAD = 18   // space above bars for count labels
const SVG_H = TOP_PAD + BAR_AREA_H + LABEL_H

interface MonthCount {
  month: number
  count: number
}

interface MonthlyChartProps {
  data: MonthCount[]
}

export function MonthlyChart({ data }: MonthlyChartProps) {
  const max = Math.max(...data.map(d => d.count), 1)
  const currentMonth = new Date().getMonth() + 1
  const colW = W / 12
  const barW = colW * 0.62
  const barPad = (colW - barW) / 2

  return (
    <svg
      viewBox={`0 0 ${W} ${SVG_H}`}
      className="w-full"
      aria-label="Gráfico de atendimentos mensais"
    >
      {data.map(({ month, count }) => {
        const i = month - 1
        const x = i * colW
        const barH = count > 0 ? Math.max((count / max) * BAR_AREA_H, 4) : 0
        const barY = TOP_PAD + BAR_AREA_H - barH
        const isCurrent = month === currentMonth
        const isPast = month < currentMonth

        const barFill = isCurrent ? '#1bb0a0' : isPast ? '#a9efe3' : '#e8f7f5'
        const labelFill = isCurrent ? '#138d83' : isPast ? '#6fe2d1' : '#cbd5e1'
        const monthFill = isCurrent ? '#138d83' : '#94a3b8'

        return (
          <g key={month}>
            {/* Bar */}
            {count > 0 && (
              <rect
                x={x + barPad}
                y={barY}
                width={barW}
                height={barH}
                rx={3}
                fill={barFill}
              />
            )}

            {/* Count label above bar */}
            {count > 0 && (
              <text
                x={x + colW / 2}
                y={barY - 3}
                textAnchor="middle"
                fontSize={7}
                fontWeight="600"
                fill={labelFill}
              >
                {count}
              </text>
            )}

            {/* Month label */}
            <text
              x={x + colW / 2}
              y={TOP_PAD + BAR_AREA_H + LABEL_H - 2}
              textAnchor="middle"
              fontSize={7.5}
              fontWeight={isCurrent ? '700' : '400'}
              fill={monthFill}
            >
              {MONTHS[i]}
            </text>
          </g>
        )
      })}

      {/* Baseline */}
      <line
        x1={0} y1={TOP_PAD + BAR_AREA_H}
        x2={W} y2={TOP_PAD + BAR_AREA_H}
        stroke="#e2e8f0"
        strokeWidth={1}
      />
    </svg>
  )
}
