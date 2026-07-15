from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import get_queried_courses, get_sections_for_courses
from solver import solve
from prefparser import classify_preferences


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this later when you have your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)

# models for incoming data
class Course(BaseModel):
    subject: str
    course_number: str
    term: str

class ScheduleRequest(BaseModel):
    course_list: list[Course]
    preferences: str | None = None

@app.get('/')
def health():
    return { 'status': 'ok' }

# maybe rename? idk
@app.post('/schedule')
def generate_schedule(request: ScheduleRequest):
    course_list = [c.model_dump() for c in request.course_list]
    sections = get_sections_for_courses(course_list) # converts from basemodel to python dict structure

    unsupported_preferences = []
    preferences = []
    if request.preferences:
        all_preferences = classify_preferences(request.preferences)
        unsupported_preferences = [p for p in all_preferences if p['type'] == 'unsupported']
        preferences = [p for p in all_preferences if p['type'] != 'unsupported']

    schedule = solve(sections, course_list, preferences)

    if schedule is None:
        return {"error": "No valid schedule found"}
    return { 'schedule': schedule, 'unsupported': unsupported_preferences }

@app.get('/courses/search')
def get_courses(q: str = ''):
    courses_raw = get_queried_courses(q)

    seen = set()
    courses = []
    for row in courses_raw:
        key = (row['subject'], row['course_number'])
        if key not in seen:
            seen.add(key)
            courses.append(row)
    
    return courses


