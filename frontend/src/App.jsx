import { useState, useEffect, useRef } from 'react'
import './App.css'

function App() {
    const [courses, setCourses] = useState([])
    const [selectedCourses, setSelectedCourses] = useState([])
    const [preferences, setPreferences] = useState('')
    const [schedule, setSchedule] = useState([])
    const [query, setQuery] = useState('')

    const generateSchedule = async () => {

        const response = await fetch(`${import.meta.env.VITE_API_URL}/schedule`, 
            {
                method: 'POST',
                headers: { 
                            'content-type': 'application/json' 
                        },
                body: JSON.stringify({course_list: selectedCourses, preferences: preferences})
            }
        )

        const data = await response.json()
        console.log(data)
        setSchedule(data)


    }

    const handleSelect = (course) => {
        setSelectedCourses([...selectedCourses, { ...course, term: 'either' }])
        setQuery('')
    }

    useEffect(() => {
        if (!query) {
            setCourses([])
            return
        }
        const fetchCourses = async () => {

            const response = await fetch(`${import.meta.env.VITE_API_URL}/courses/search?q=${query}`, 
                {
                    method: 'GET',
                    headers: { 
                                'content-type': 'application/json' 
                            },
                }
            )
            if (!response.ok) {
                console.log('error')
                return 
            }
            const data = await response.json()
            setCourses(data)
        }
        fetchCourses()

    }, [query])

    const inputRef = useRef(null)


    return (
        <div>
            <div className="input-container" onClick={() => inputRef.current.focus()}>
                {selectedCourses.map(course => (
                    <span key={`${course.subject}-${course.course_number}`} className="pill">
                        {course.subject} {course.course_number}
                        <button onClick={() => setSelectedCourses(selectedCourses.filter(c => c !== course))}>×</button>
                    </span>
                ))}
                <input
                    ref={inputRef}
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onBlur={() => setTimeout(() => setCourses([]), 150)}
                />
            </div>
            {courses.length > 0 && (
                    <div>
                    {courses.map(course => (
                        <div key={`${course.subject}-${course.course_number}`} onClick={() => handleSelect(course)}>
                            {course.subject} {course.course_number}
                        </div>
                    ))}
                    </div>
    
            )}
            <button onClick={generateSchedule}>generate schedule</button>
            {schedule && !schedule.error && (
                <div>
                    {Object.entries(schedule).map(([key, section]) => (
                        <div key={key}>
                            <strong>{section.subject} {section.course_number} - {section.format}</strong>
                            <p>{section.section} | {section.status}</p>
                            {section.meetings?.map((m, i) => (
                                <p key={i}>{m.days} {m.startTime} - {m.endTime} {m.startDate} </p>
                            ))}
                        </div>
                    ))}
                </div>
            )}
            {schedule?.error && <p>{schedule.error}</p>}
        </div>

    )
}

export default App
