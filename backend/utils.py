
from datetime import date

def parse_time(time_str):
    if not time_str:
        return None
    
    time_str = time_str.strip().lower()
    is_pm = 'p.m.' in time_str
    is_am = 'a.m.' in time_str

    time_str = time_str.replace('a.m.', '').replace('p.m.', '').strip()
    parts = time_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1]) if len(parts) > 1 else 0

    if is_pm and hours != 12:
        hours += 12
    if is_am and hours == 12:
        hours = 0
    
    return hours * 60 + minutes


def dates_overlap(m1, m2):
    start1 = date.fromisoformat(m1['startDate'])
    end1 = date.fromisoformat(m1['endDate'])
    start2 = date.fromisoformat(m2['startDate'])
    end2 = date.fromisoformat(m2['endDate'])
    
    return start1 <= end2 and start2 <= end1

def meetings_overlap(m1, m2):
    if not m1['days'] or not m2['days']:
        return False
    
    days1 = set(m1['days'].split())
    days2 = set(m2['days'].split())
    if not days1 & days2:
        return False
    
    if not dates_overlap(m1, m2):
        return False
    
    start1 = parse_time(m1['startTime'])
    end1 = parse_time(m1['endTime'])
    start2 = parse_time(m2['startTime'])
    end2 = parse_time(m2['endTime'])
    
    return start1 < end2 and start2 < end1