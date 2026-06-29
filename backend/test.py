from solver import solve

# 1 conflicting section pair 
sections = [
    {
        'subject': 'CPSC_V',
        'course_number': '110',
        'format': 'Lecture',
        'meetings': [{'days': 'Mon Wed Fri', 'startTime': '9:00 a.m.', 'endTime': '10:00 a.m.', 'startDate': '2026-09-08', 'endDate': '2026-12-01'}]
    },
    {
        'subject': 'CPSC_V',
        'course_number': '110',
        'format': 'Lecture',
        'meetings': [{'days': 'Mon Wed Fri', 'startTime': '11:00 a.m.', 'endTime': '12:00 p.m.', 'startDate': '2026-09-08', 'endDate': '2026-12-01'}]
    },
    {
        'subject': 'MATH_V',
        'course_number': '100',
        'format': 'Lecture',
        'meetings': [{'days': 'Mon Wed Fri', 'startTime': '9:00 a.m.', 'endTime': '10:00 a.m.', 'startDate': '2026-09-08', 'endDate': '2026-12-01'}]
    },
    {
        'subject': 'MATH_V',
        'course_number': '100',
        'format': 'Lecture',
        'meetings': [{'days': 'Mon Wed Fri', 'startTime': '11:00 a.m.', 'endTime': '12:00 p.m.', 'startDate': '2026-09-08', 'endDate': '2026-12-01'}]
    },
]

result = solve(sections)
print(result)

# no possible schedule 
sections_impossible = [
    {
        'subject': 'CPSC_V',
        'course_number': '110',
        'format': 'Lecture',
        'meetings': [{'days': 'Mon Wed Fri', 'startTime': '9:00 a.m.', 'endTime': '10:00 a.m.', 'startDate': '2026-09-08', 'endDate': '2026-12-01'}]
    },
    {
        'subject': 'MATH_V',
        'course_number': '100',
        'format': 'Lecture',
        'meetings': [{'days': 'Mon Wed Fri', 'startTime': '9:00 a.m.', 'endTime': '10:00 a.m.', 'startDate': '2026-09-08', 'endDate': '2026-12-01'}]
    },
]

result = solve(sections_impossible)
print(result)  # should print None