import { useState, useEffect, useRef } from 'react'
import './App.css'
import ScheduleGrid from './ScheduleGrid'

function App() {
    // courses displayed/responding to user query
    const [courses, setCourses] = useState([])
    // actual chosen courses out of the responding to query
    const [selectedCourses, setSelectedCourses] = useState([])
    const [preferences, setPreferences] = useState('')
    const [schedule, setSchedule] = useState([])
    // user typed course 
    const [courseQuery, setCourseQuery] = useState('')

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
        console.log(data.schedule)
        setSchedule(data.schedule)
        // TODO: manage unsupported


    }

    const handleSelect = (course) => {
        setSelectedCourses([...selectedCourses, { ...course, term: 'either' }])
        setCourseQuery('')
    }

    useEffect(() => {
        if (!courseQuery) {
            setCourses([])
            return
        }
        const fetchCourses = async () => {

            const response = await fetch(`${import.meta.env.VITE_API_URL}/courses/search?q=${courseQuery}`, 
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

    }, [courseQuery])

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
                    value={courseQuery}
                    onChange={(e) => setCourseQuery(e.target.value)}
                    onBlur={() => setTimeout(() => setCourses([]), 150)}
                />
            </div>
            {courses.length > 0 && (
                    <div>
                    {courses.map(course => (
                        <div key={`${course.subject}-${course.course_number}`} onMouseDown={() => handleSelect(course)}>
                            {course.subject} {course.course_number}
                        </div>
                    ))}
                    </div>
    
            )}

            <input 
                type="text" 
                placeholder="schedule preferences (ex. no classes thursday, minimize gaps between classes, mostly morning classes)"
                value={preferences}
                onChange={(e)=>setPreferences(e.target.value)}
            />

            <button onClick={generateSchedule}>generate schedule</button>
            {schedule && !schedule.error && <ScheduleGrid schedule={schedule} />}
            {schedule?.error && <p>{schedule.error}</p>}
        </div>

    )
}

export default App
