from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

def get_sections_for_courses(course_list):
    sections = []

    for course in course_list:
        subject = course['subject'] + '_V'

        response = supabase.table('sections') \
                        .select('*') \
                        .eq('subject', subject) \
                        .eq('course_number', course['course_number']) \
                        .execute()
        
        sections.extend(response.data)

    return sections

def get_queried_courses(q):
    q = q.strip()
    parts = q.split()
    
    if len(parts) == 2:
        # user typed "CPSC 110" — match both
        subject, number = parts
        response = (supabase.table('sections')
            .select('subject, course_number, title')
            .ilike('subject', f'{subject}%')
            .ilike('course_number', f'{number}%')
            .execute())
    else:
        # single term — search both fields separately and combine
        r1 = (supabase.table('sections')
            .select('subject, course_number, title')
            .ilike('subject', f'{q}%')
            .execute())
        r2 = (supabase.table('sections')
            .select('subject, course_number, title')
            .ilike('course_number', f'{q}%')
            .execute())
        response_data = r1.data + r2.data
        for row in response_data:
            row['subject'] = row['subject'].replace('_V', '')
        return response_data
    
    for row in response.data:
        row['subject'] = row['subject'].replace('_V', '')
    return response.data


    


        