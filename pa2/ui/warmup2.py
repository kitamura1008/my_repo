import sqlite3

conn = sqlite3.connect('course_information.sqlite3')
cur = conn.cursor()

q1 = "SELECT * FROM courses WHERE dept = ?"
res1 = cur.execute(q1, ["CMSC"])
result1 = res1.fetchall()

print('result1')
print(result1)
print()

q2 = "SELECT dept, course_num, section_num FROM courses INNER JOIN sections \
      ON courses.course_id = sections.course_id INNER JOIN meeting_patterns \
      ON  sections.meeting_pattern_id =  meeting_patterns.meeting_pattern_id \
      WHERE meeting_patterns.day = ? AND meeting_patterns.time_start = ?"
res2 = cur.execute(q2, ['MWF', '1030'])
result2 = res2.fetchall()

print('result2')
print(result2)
print()

q3 = 'SELECT dept, course_num FROM courses INNER JOIN sections \
      ON courses.course_id = sections.course_id INNER JOIN meeting_patterns \
      ON sections.meeting_pattern_id = meeting_patterns.meeting_pattern_id \
      WHERE meeting_patterns.day = ? AND meeting_patterns.time_start >= ? \
      AND meeting_patterns.time_end <= ? AND sections.building_code = ?'
res3 = cur.execute(q3, ['MWF', '1030', '1500', 'RY'])
result3 = res3.fetchall()

print('result3')
print(result3)
print()

q4 = 'SELECT dept, course_num, title FROM courses INNER JOIN sections \
      ON courses.course_id = sections.course_id INNER JOIN meeting_patterns \
      ON sections.meeting_pattern_id = meeting_patterns.meeting_pattern_id \
      INNER JOIN catalog_index ON catalog_index.course_id = courses.course_id \
      WHERE (meeting_patterns.day = ? AND meeting_patterns.time_start = ?) \
      AND (catalog_index.word = ? OR catalog_index.word = ?) \
      GROUP BY catalog_index.course_id HAVING count(catalog_index.course_id)=2'
res4 = cur.execute(q4, ['MWF', '930', 'programming', 'abstraction'])
result4 = res4.fetchall()

print('result4')
print(result4)
print()

conn.close()