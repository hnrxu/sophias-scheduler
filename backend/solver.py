from utils import meetings_overlap, parse_time
from ortools.sat.python import cp_model

TIME_OF_DAY = {
    'morning': ('8:00 a.m.', '12:00 p.m.'),
    'afternoon': ('12:00 p.m.', '5:00 p.m.'),
    'evening': ('5:00 p.m.', '9:00 p.m.')
}

# checks if sections 1 and 2 have conflicting times
def sections_conflict(s1, s2):
    for m1 in s1['meetings']:
        for m2 in s2['meetings']:
            if meetings_overlap(m1, m2):
                return True
    return False

# separates list of sections into groups of same course and type (ex. 'CPSC_V-110-Lecture': [s1, s2, s3], 'CPSC_V-110-Laboratory': [s4, s5] )
def group_sections(sections):
    groups = {}

    for section in sections:
        key = f"{section['subject']}-{section['course_number']}-{section['format']}"

        if key not in groups:
            groups[key] = []
        groups[key].append(section)

    return groups

# after db return, filter by user requests for term-specific courses
def filter_by_term(sections, course_list):
    term_map = {}
    for course in course_list:
        term_map[(course['subject'], course['course_number'])] = course['term']

    filtered_sections = []
    for section in sections:
        term = term_map.get((section['subject'].replace('_V', ''), section['course_number']))
        if term == 'either':
            filtered_sections.append(section)
        elif term == '1':
            # term 1 sections start in sep
            for m in section['meetings']:
                if m['startDate'].startswith('2026-09') or m['startDate'].startswith('2026-08'):
                    filtered_sections.append(section)
                    break
        elif term == '2':
            # term 2 sections start in jan
            for m in section['meetings']:
                if m['startDate'].startswith('2027-01'): 
                    filtered_sections.append(section)
                    break
    return filtered_sections


def filter_open(sections):
    filtered_sections = []
    for section in sections:
        if section['status'] == 'Open':
            filtered_sections.append(section)
    return filtered_sections


def add_start_after_objective(model, section_options, variables, time_str, days=None):
    penalties = []
    cutoff = parse_time(time_str)
    for key, options in section_options.items():
        for idx, section in enumerate(options):
            for meeting in section['meetings']:
                if not meeting['startTime']:
                    continue

                meeting_days = set((meeting['days'] or '').split())
                # preference no effect
                if days and not meeting_days.intersection(set(days)):
                    continue

                section_start = parse_time(meeting['startTime']) 
                # section starts before supposed to
                # TODO: check whether the start should iclude cutoff or not
                if section_start < cutoff:
                    is_chosen = model.new_bool_var(f'{key}_{idx}_excluded_day')
                    model.add(variables[key] == idx).only_enforce_if(is_chosen)
                    model.add(variables[key] != idx).only_enforce_if(is_chosen.Not())
                    penalties.append(is_chosen)
                    break
    return penalties


def add_end_before_objective(model, section_options, variables, time_str, days=None):
    penalties = []
    cutoff = parse_time(time_str)
    for key, options in section_options.items():
        for idx, section in enumerate(options):
            for meeting in section['meetings']:
                if not meeting['endTime']:
                    continue

                meeting_days = set((meeting['days'] or '').split())
                # preference no effect
                if days and not meeting_days.intersection(set(days)):
                    continue

                section_end = parse_time(meeting['endTime']) 
                # section ends after supposed to
                # TODO: check whether the start should iclude cutoff or not
                if section_end > cutoff:
                    is_chosen = model.new_bool_var(f'{key}_{idx}_excluded_day')
                    model.add(variables[key] == idx).only_enforce_if(is_chosen)
                    model.add(variables[key] != idx).only_enforce_if(is_chosen.Not())
                    penalties.append(is_chosen)
                    break
    return penalties


def add_free_block_objective(model, section_options, variables, start_time_str, end_time_str, days=None):
    penalties = []
    cutoff_start = parse_time(start_time_str)
    cutoff_end = parse_time(end_time_str)
    for key, options in section_options.items():
        for idx, section in enumerate(options):
            for meeting in section['meetings']:
                if not meeting['startTime'] or not meeting['endTime']:
                    continue

                meeting_days = set((meeting['days'] or '').split())
                # preference no effect
                if days and not meeting_days.intersection(set(days)):
                    continue

                section_start = parse_time(meeting['startTime']) 
                section_end = parse_time(meeting['endTime']) 

                # section ends after supposed to
                # TODO: check whether the start should iclude cutoff or not
                if section_start < cutoff_end and cutoff_start < section_end:
                    is_chosen = model.new_bool_var(f'{key}_{idx}_excluded_block')
                    model.add(variables[key] == idx).only_enforce_if(is_chosen)
                    model.add(variables[key] != idx).only_enforce_if(is_chosen.Not())
                    penalties.append(is_chosen)
                    break
    return penalties


    
def add_avoid_days_objective(model, section_options, variables, days):
    day_set = set(days)
    penalties = []
    for key, options in section_options.items():
        for idx, section in enumerate(options):
            for meeting in section['meetings']:
                meeting_days = set((meeting['days'] or '').split())
                if day_set.intersection(meeting_days):
                    is_chosen = model.new_bool_var(f'{key}_{idx}_excluded_day')
                    model.add(variables[key] == idx).only_enforce_if(is_chosen)
                    model.add(variables[key] != idx).only_enforce_if(is_chosen.Not())
                    penalties.append(is_chosen)
                    break
    return penalties

def add_prefer_days_objective(model, section_options, variables, days):
    day_set = set(days)
    penalties = []
    for key, options in section_options.items():
        for idx, section in enumerate(options):
            has_preferred_day = False
            for meeting in section['meetings']:
                meeting_days = set((meeting['days'] or '').split())
                if  day_set.intersection(meeting_days):
                    has_preferred_day = True
            if not has_preferred_day:
                is_chosen = model.new_bool_var(f'{key}_{idx}_included_day')
                model.add(variables[key] == idx).only_enforce_if(is_chosen)
                model.add(variables[key] != idx).only_enforce_if(is_chosen.Not())
                penalties.append(is_chosen)
                    
    return penalties



def add_avoid_time_objective(model, section_options, variables, period, days=None):
    penalties = []
    start_str, end_str = TIME_OF_DAY[period]
    start = parse_time(start_str)
    end = parse_time(end_str)

    for key, options in section_options.items():
        for idx, section in enumerate(options):
            for meeting in section['meetings']:

                if not meeting['startTime'] or not meeting['endTime']:
                    continue

                meeting_days = set((meeting['days'] or '').split())
                # preference no effect
                if days and not meeting_days.intersection(set(days)):
                    continue

                section_start = parse_time(meeting['startTime'])
                section_end = parse_time(meeting['endTime'])

                if  section_start >= start and section_end <= end:
                    is_chosen = model.new_bool_var(f'{key}_{idx}_excluded_{period}')
                    model.add(variables[key] == idx).only_enforce_if(is_chosen)
                    model.add(variables[key] != idx).only_enforce_if(is_chosen.Not())
                    penalties.append(is_chosen)
                    break

    return penalties

def add_prefer_time_objective(model, section_options, variables, period, days=None):
    penalties = []
    start_str, end_str = TIME_OF_DAY[period]
    start = parse_time(start_str)
    end = parse_time(end_str)

    for key, options in section_options.items():
        for idx, section in enumerate(options):
            has_preferred_period = False
            for meeting in section['meetings']:

                if not meeting['startTime'] or not meeting['endTime']:
                    continue

                meeting_days = set((meeting['days'] or '').split())
                # preference no effect
                if days and not meeting_days.intersection(set(days)):
                    continue

                section_start = parse_time(meeting['startTime'])
                section_end = parse_time(meeting['endTime'])

                if  section_start >= start and section_end <= end:
                    has_preferred_period = True

            if not has_preferred_period:
                is_chosen = model.new_bool_var(f'{key}_{idx}_excluded_{period}')
                model.add(variables[key] == idx).only_enforce_if(is_chosen)
                model.add(variables[key] != idx).only_enforce_if(is_chosen.Not())
                penalties.append(is_chosen)
            

    return penalties

# returns gap in minutes between two sections, 0 if they don't share a day or overlap
def compute_gap(s1, s2):
    gap = 0
    for m1 in s1['meetings']:
        for m2 in s2['meetings']:
            if not m1['startTime'] or not m2['startTime']:
                continue
            days1 = set((m1['days'] or '').split())
            days2 = set((m2['days'] or '').split())
            if not days1.intersection(days2):
                continue
            start1, end1 = parse_time(m1['startTime']), parse_time(m1['endTime'])
            start2, end2 = parse_time(m2['startTime']), parse_time(m2['endTime'])
            g = max(start2 - end1, start1 - end2, 0)
            gap += g
    return gap

def add_minimize_gaps_objective(model, section_options, variables):
    gap_vars = []
    keys = list(section_options.keys())
    for i in range(len(keys)):
        for j in range(i+1, len(keys)):

            key1, key2 = keys[i], keys[j]
            options1, options2 = section_options[key1], section_options[key2]
            
            gaps = []
            for section1 in options1:
                for section2 in options2:
                    gap = compute_gap(section1, section2)
                    gaps.append(gap)

            if all(g == 0 for g in gaps):
                continue  # no gaps between these 2 courses (regardless of section), skip
            

            combined = model.new_int_var(0, len(options1)*len(options2)-1, f'{key1}_{key2}_combined')
            # set combined to the appropriate index/gap of gaps based on the chosen sections (var[key1] & var[key2])
            model.add(combined == variables[key1] * len(options2) + variables[key2])

            gap_var = model.new_int_var(0, max(gaps), f'{key1}_{key2}_gap')
            # sets gap var to gaps[combined] (appropriate index of gaps corresponding to the chosen sections)
            model.add_element(combined, gaps, gap_var)
             
            # scale gap minutes to be comparable to boolean penalties
            # e.g. every 60 min of gap = 1 penalty unit
            scaled_gap = model.new_int_var(0, 8, f'{key1}_{key2}_scaled_gap')
            model.add_division_equality(scaled_gap, gap_var, 60)
            gap_vars.append(scaled_gap)

    return gap_vars
        
        

            
# TODO: add smth if smth the student chose is closed

def solve(sections, course_list, preferences=None):
    model = cp_model.CpModel()

    og_section_options = group_sections(sections)

    # required filters
    sections = filter_by_term(sections, course_list)
    sections = filter_open(sections)



    start_after_constraint = None
    end_before_constraint = None
    free_block_constraint = None
    avoid_days_constraint = None
    prefer_days_constraint = None
    avoid_time_constraint = None
    prefer_time_constraint = None
    minimize_gaps_constraint = None
    if preferences:
        for constraint in preferences:
            if constraint['type'] == 'start_after':
                start_after_constraint = constraint
            elif constraint['type'] == 'end_before':
                end_before_constraint = constraint
            elif constraint['type'] == 'free_block':
                free_block_constraint = constraint
            elif constraint['type'] == 'avoid_days':
                avoid_days_constraint = constraint
            elif constraint['type'] == 'prefer_days':
                prefer_days_constraint = constraint
            elif constraint['type'] == 'avoid_time':
                avoid_time_constraint = constraint
            elif constraint['type'] == 'prefer_time':
                prefer_time_constraint = constraint
            elif constraint['type'] == 'minimize_gaps':
                minimize_gaps_constraint = constraint
            # etc for other filters


    section_options = group_sections(sections)

    # check if all required sections still there
    for key in og_section_options.keys():
        if key not in section_options:
            return None
        
    
    # creats one variable per grp of options
    variables = {}
    for key, options in section_options.items():
        if not options:
            return None # return impossible schedule if no sections in a grp
        # creates a 'decision variable' ex variables[cpsc 110 lecture] = some value from 0-optionssize
        variables[key] = model.new_int_var(0, len(options) - 1, key)
    

    # add forbidden combinations for conflicting times
    keys = list(section_options.keys())
    for i in range(len(keys)):
        for j in range(i+1, len(keys)):
            forbidden = []

            key1 = keys[i]
            key2 = keys[j]

            options1 = section_options[key1]
            options2 = section_options[key2]

            for index1, section1 in enumerate(options1):
                for index2, section2 in enumerate(options2):
                    if sections_conflict(section1, section2):
                        forbidden.append([index1, index2]) # set this pair of sections is forbidden
            
            if forbidden:
                model.add_forbidden_assignments([variables[key1], variables[key2]], forbidden)

    penalties = []
    if start_after_constraint:
        penalties.extend(add_start_after_objective(model, section_options, variables, start_after_constraint['time'], start_after_constraint.get('days')))
    if end_before_constraint:
        penalties.extend(add_end_before_objective(model, section_options, variables, end_before_constraint['time'], end_before_constraint.get('days')))
    if free_block_constraint:
        penalties.extend(add_free_block_objective(model, section_options, variables, free_block_constraint['start_time'], free_block_constraint['end_time'], free_block_constraint.get('days')))
    if avoid_days_constraint:
        penalties.extend(add_avoid_days_objective(model, section_options, variables, avoid_days_constraint['days']))
    if prefer_days_constraint:
        penalties.extend(add_prefer_days_objective(model, section_options, variables, prefer_days_constraint['days']))
    if avoid_time_constraint:
        penalties.extend(add_avoid_time_objective(model, section_options, variables, avoid_time_constraint['period'], avoid_time_constraint.get('days')))
    if prefer_time_constraint:
        penalties.extend(add_prefer_time_objective(model, section_options, variables, prefer_time_constraint['period'], prefer_time_constraint.get('days')))
    if minimize_gaps_constraint:
        penalties.extend(add_minimize_gaps_objective(model, section_options, variables))

    if penalties:
        model.minimize(sum(penalties))

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        results = {}
        for key, index_option in variables.items():
            results[key] = section_options[key][solver.value(index_option)]
        return results
    return None

