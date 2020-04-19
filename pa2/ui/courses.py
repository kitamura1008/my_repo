'''
Course search engine: search

Tetsuo Fujino
Takayuki Kitamura
'''

from math import radians, cos, sin, asin, sqrt, ceil
import sqlite3
import os


# Use this filename for the database
DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'course_information.sqlite3')


def find_courses(args_from_ui):
    '''
    Takes a dictionary containing search criteria and returns courses
    that match the criteria.  The dictionary will contain some of the
    following fields:

      - dept a string
      - day is list of strings
           -> ["'MWF'", "'TR'", etc.]
      - time_start is an integer in the range 0-2359
      - time_end is an integer an integer in the range 0-2359
      - enrollment is a pair of integers
      - walking_time is an integer
      - building_code ia string
      - terms is a list of strings string: ["quantum", "plato"]

    Returns a pair: an ordered list of attribute names and a list the
     containing query results.  Returns ([], []) when the dictionary
     is empty.
    '''
    assert_valid_input(args_from_ui)

    if args_from_ui == {}:
        return ([], [])

    conn = sqlite3.connect(DATABASE_FILENAME)
    cur = conn.cursor()

    columns_tables = select_column_table(args_from_ui)
    condition_str, args_lst = make_condition(args_from_ui, conn)

    query = columns_tables + 'WHERE ' + condition_str
    result = cur.execute(query, args_lst)
    header = get_header(result)
    contents = result.fetchall()
    return (header, contents)


########### auxiliary functions #################
def select_column_table(args_from_ui):
    '''
    Make a part of query to select columns and tables to be joined

    Input: a dictionary containing search criteria and returns courses
        that match the criteria.
        Also refer to the docstring for find_courses(args_from_ui)

    Output:(string) a part of query to select columns and tables

    '''
    columns = 'dept, course_num, title'
    columns_middle = columns + ', section_num, day, time_start, time_end, enrollment'

    tbl_query = ''
    tbl_query_middle = 'JOIN sections ON courses.course_id = sections.course_id\
                        JOIN meeting_patterns ON sections.meeting_pattern_id = \
                        meeting_patterns.meeting_pattern_id '

    if 'terms' in args_from_ui:
        tbl_query += 'LEFT OUTER JOIN sections ON courses.course_id = sections.course_id\
                      JOIN catalog_index ON catalog_index.course_id = courses.course_id '
        tbl_query_middle += 'JOIN catalog_index ON catalog_index.course_id = courses.course_id '


    if 'building_code' in args_from_ui:
        columns = columns_middle + ', a.building_code, \
                  time_between(a.lon, a.lat, b.lon, b.lat) AS walking_time'
        tbl_query = tbl_query_middle + 'JOIN (SELECT building_code, lon, lat FROM gps) AS a \
                                        ON sections.building_code = a.building_code\
                                        JOIN (SELECT building_code, lon, lat FROM gps \
                                        WHERE building_code = ?) AS b '

    elif ('day' in args_from_ui) or ('enrollment' in args_from_ui) or (
            'time_start' in args_from_ui) or ('time_end' in args_from_ui):
        columns = columns_middle
        tbl_query = tbl_query_middle

    col_query = 'SELECT {} FROM courses '.format(columns)
    return col_query + tbl_query


def make_condition(args_from_ui, conn):
    '''
    Make a part of query to set conditions to select relevant rows

    Input:
        args_from_ui:
            a dictionary containing search criteria and returns courses
            that match the criteria.
            Also refer to the docstring for find_courses(args_from_ui)
        conn:
            a connection object

    Output:(a pair)
        condition_str: (string) a part of query to be used to select columns and tables
        args_lst: (list) list of arguments to be put into a query
    '''

    condition_lst = []
    args_lst = []
    day_terms = {'day':'meeting_patterns.day = ?',
                 'terms':'catalog_index.word = ?'}
    others = {'dept':'courses.dept = ?',
              'time_start':'meeting_patterns.time_start >= ?',
              'time_end':'meeting_patterns.time_end <= ?',
              'enrollment':
              '(sections.enrollment >= ? AND sections.enrollment <= ?)',
              'walking_time':'time_between(a.lon, a.lat, b.lon, b.lat) <= ?'}
    for key in args_from_ui:
        if key in others:
            condition_lst.append(others[key])
            if isinstance(args_from_ui[key], list):
                for value in args_from_ui[key]:
                    args_lst.append(value)
            else:
                args_lst.append(args_from_ui[key])

        elif key in day_terms:
            condition = []
            for i, j in enumerate(args_from_ui[key]):
                condition.append(day_terms[key])
                args_lst.append(j)
            condition = ' OR '.join(condition)
            condition = '(' + condition + ')'
            if key == 'terms':
                condition += ' GROUP BY catalog_index.course_id, sections.section_num\
                               HAVING count(catalog_index.course_id)={}'.format(i + 1)
            condition_lst.append(condition)

        else:
            conn.create_function('time_between', 4, compute_time_between)
            args_lst.insert(0, args_from_ui[key])

    condition_str = ' AND '.join(condition_lst)
    return condition_str, args_lst

########### do not change this code #############

def assert_valid_input(args_from_ui):
    '''
    Verify that the input conforms to the standards set in the
    assignment.
    '''

    assert isinstance(args_from_ui, dict)

    acceptable_keys = set(['time_start', 'time_end', 'enrollment', 'dept',
                           'terms', 'day', 'building_code', 'walking_time'])
    assert set(args_from_ui.keys()).issubset(acceptable_keys)

    # get both buiding_code and walking_time or neither
    has_building = ("building_code" in args_from_ui and
                    "walking_time" in args_from_ui)
    does_not_have_building = ("building_code" not in args_from_ui and
                              "walking_time" not in args_from_ui)

    assert has_building or does_not_have_building

    assert isinstance(args_from_ui.get("building_code", ""), str)
    assert isinstance(args_from_ui.get("walking_time", 0), int)

    # day is a list of strings, if it exists
    assert isinstance(args_from_ui.get("day", []), (list, tuple))
    assert all([isinstance(s, str) for s in args_from_ui.get("day", [])])

    assert isinstance(args_from_ui.get("dept", ""), str)

    # terms is a non-empty list of strings, if it exists
    terms = args_from_ui.get("terms", [""])
    assert terms
    assert isinstance(terms, (list, tuple))
    assert all([isinstance(s, str) for s in terms])

    assert isinstance(args_from_ui.get("time_start", 0), int)
    assert args_from_ui.get("time_start", 0) >= 0

    assert isinstance(args_from_ui.get("time_end", 0), int)
    assert args_from_ui.get("time_end", 0) < 2400

    # enrollment is a pair of integers, if it exists
    enrollment_val = args_from_ui.get("enrollment", [0, 0])
    assert isinstance(enrollment_val, (list, tuple))
    assert len(enrollment_val) == 2
    assert all([isinstance(i, int) for i in enrollment_val])
    assert enrollment_val[0] <= enrollment_val[1]


def compute_time_between(lon1, lat1, lon2, lat2):
    '''
    Converts the output of the haversine formula to walking time in minutes
    '''
    meters = haversine(lon1, lat1, lon2, lat2)

    # adjusted downwards to account for manhattan distance
    walk_speed_m_per_sec = 1.1
    mins = meters / (walk_speed_m_per_sec * 60)

    return int(ceil(mins))


def haversine(lon1, lat1, lon2, lat2):
    '''
    Calculate the circle distance between two points
    on the earth (specified in decimal degrees)
    '''
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))

    # 6367 km is the radius of the Earth
    km = 6367 * c
    m = km * 1000
    return m


def get_header(cursor):
    '''
    Given a cursor object, returns the appropriate header (column names)
    '''
    header = []

    for i in cursor.description:
        s = i[0]
        if "." in s:
            s = s[s.find(".")+1:]
        header.append(s)

    return header
