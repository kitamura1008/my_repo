
SELECT * FROM courses WHERE dept = "CMSC";

SELECT dept, course_num, section_num
FROM courses
INNER JOIN sections
ON courses.course_id = sections.course_id
INNER JOIN meeting_patterns
ON  sections.meeting_pattern_id =  meeting_patterns.meeting_pattern_id
WHERE meeting_patterns.day = 'MWF' AND meeting_patterns.time_start = '1030';

SELECT dept, course_num
FROM courses
INNER JOIN sections
ON courses.course_id = sections.course_id
INNER JOIN meeting_patterns
ON sections.meeting_pattern_id = meeting_patterns.meeting_pattern_id
WHERE meeting_patterns.day = 'MWF' AND meeting_patterns.time_start >= '1030' AND meeting_patterns.time_end <= '1500' AND sections.building_code = 'RY';


SELECT dept, course_num, title
FROM courses
INNER JOIN sections
ON courses.course_id = sections.course_id
INNER JOIN meeting_patterns
ON sections.meeting_pattern_id = meeting_patterns.meeting_pattern_id
INNER JOIN catalog_index
ON catalog_index.course_id = courses.course_id
WHERE (meeting_patterns.day = 'MWF' AND meeting_patterns.time_start = '930') AND
(catalog_index.word = 'programming' OR catalog_index.word = 'abstraction') 
GROUP BY catalog_index.course_id
HAVING count(catalog_index.course_id)=2;