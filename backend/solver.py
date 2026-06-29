from utils import meetings_overlap
from ortools.sat.python import cp_model

# checks if sections 1 and 2 have conflicting times
def sections_conflict(s1, s2):
    for m1 in s1['meetings']:
        for m2 in s2['meetings']:
            if meetings_overlap(m1, m2):
                return True
    return False

# separates list of sections into groups of same course and type (ex. 'CPSC_V-110-Lecture': [s1, s2, s3], 'CPSC_V-110-Laboratory': [s4, s5] )
def group_sections(sections, preferences=None):
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


def solve(sections, course_list):
    sections = filter_by_term(sections, course_list)
    sections = filter_open(sections)
    section_options = group_sections(sections)
    model = cp_model.CpModel()

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


    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        results = {}
        for key, index_option in variables.items():
            results[key] = section_options[key][solver.value(index_option)]
        return results
    return None

