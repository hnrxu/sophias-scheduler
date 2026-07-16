import { useMemo } from 'react'
import './ScheduleGrid.css'

const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const START_HOUR = 7
const END_HOUR = 24
const TOTAL_MINS = (END_HOUR - START_HOUR) * 60

const COLORS = {
  1: { bg: '#dbeafe', text: '#1e40af', border: '#93c5fd' },
  2: { bg: '#dcfce7', text: '#166534', border: '#86efac' },
}

function parseMinutes(timeStr) {
  if (!timeStr) return null
  const lower = timeStr.toLowerCase()
  const isPm = lower.includes('p.m.')
  const clean = lower.replace('a.m.', '').replace('p.m.', '').trim()
  const [h, m] = clean.split(':').map(Number)
  let hours = h
  if (isPm && h !== 12) hours += 12
  if (!isPm && h === 12) hours = 0
  return hours * 60 + m
}

function getTerm(section) {
  for (const m of section.meetings || []) {
    if (m.startDate?.startsWith('2026')) return 1
    if (m.startDate?.startsWith('2027')) return 2
  }
  return 1
}

export default function ScheduleGrid({ schedule }) {
  const blocks = useMemo(() => {
    if (!schedule) return []
    return Object.values(schedule).flatMap(section => {
      const term = getTerm(section)
      return (section.meetings || []).flatMap(meeting => {
        if (!meeting.days || !meeting.startTime || !meeting.endTime) return []
        const start = parseMinutes(meeting.startTime)
        const end = parseMinutes(meeting.endTime)
        if (start === null || end === null) return []
        return meeting.days.split(' ').map(day => ({
          day, start, end,
          label: `${section.subject.replace('_V', '')} ${section.course_number}`,
          sublabel: section.format,
          term,
        }))
      })
    })
  }, [schedule])

  const timeLabels = []
  for (let h = START_HOUR; h <= END_HOUR; h++) {
    timeLabels.push(h === 12 ? '12pm' : h > 12 ? `${h - 12}pm` : `${h}am`)
  }

  return (
    <div className="schedule-wrapper">
      <div className="schedule-grid">
        <div />
        {DAYS.map(d => (
          <div key={d} className="day-header">{d}</div>
        ))}

        <div className="time-column">
          {timeLabels.map((label, i) => (
            <div key={i} className="time-label">{label}</div>
          ))}
        </div>

        {DAYS.map(day => (
          <div key={day} className="day-column">
            {timeLabels.map((_, i) => (
              <div key={i} className="time-slot" />
            ))}
            {blocks.filter(b => b.day === day).map((b, i) => {
              const top = ((b.start - START_HOUR * 60) / TOTAL_MINS) * 100
              const height = ((b.end - b.start) / TOTAL_MINS) * 100
              const color = COLORS[b.term] || COLORS[1]
              return (
                <div key={i} className="block" style={{
                  top: `${top}%`,
                  height: `${height}%`,
                  background: color.bg,
                  border: `1px solid ${color.border}`,
                  color: color.text,
                }}>
                  <div className="block-label">{b.label}</div>
                  <div className="block-sublabel">{b.sublabel}</div>
                </div>
              )
            })}
          </div>
        ))}
      </div>

      <div className="legend">
        {[1, 2].map(term => (
          <span key={term} className="legend-item">
            <span className="legend-dot" style={{ background: COLORS[term].bg, border: `1px solid ${COLORS[term].border}` }} />
            Term {term}
          </span>
        ))}
      </div>
    </div>
  )
}