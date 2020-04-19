"""
CAPP 30122: Course Search Engine Part 1

Takayuki Kitamura
"""
# DO NOT REMOVE THESE LINES OF CODE
# pylint: disable-msg=invalid-name, redefined-outer-name, unused-argument, unused-variable

import queue
import json
import sys
import csv
import re
import bs4
import util

INDEX_IGNORE = set(['a', 'also', 'an', 'and', 'are', 'as', 'at', 'be',
                    'but', 'by', 'course', 'for', 'from', 'how', 'i',
                    'ii', 'iii', 'in', 'include', 'is', 'not', 'of',
                    'on', 'or', 's', 'sequence', 'so', 'social', 'students',
                    'such', 'that', 'the', 'their', 'this', 'through', 'to',
                    'topics', 'units', 'we', 'were', 'which', 'will', 'with',
                    'yet'])

def get_html_text(url):
    '''
    Get html texts and associated url of a web page.

    Inputs:
        url: an url of a web page.

    Outputs:
        html text and associated url of the web page.
    '''
    request_ob = util.get_request(url)
    if request_ob is None:
        return None
    request_ob_text = util.read_request(request_ob)
    associated_url = util.get_request_url(request_ob)
    return request_ob_text, associated_url


def get_link_lst(soup, parent_url, limiting_domain):
    '''
    Get a link list on a web page.

    Inputs:
        soup: soup object
        parent_url: URL of the web page from you want to get a link list
        limiting_domain: a specific domain of web pages you should visit

    Outputs:
        a link list on the web page.
    '''
    orginal_link_lst = soup.find_all('a')
    link_lst = []
    for link in orginal_link_lst:
        l = link.get('href')
        if l is None:
            continue
        l = util.remove_fragment(l)
        if not util.is_absolute_url(l):
            l = util.convert_if_relative_url(parent_url, l)
            if l is None:
                continue
        if (util.is_url_ok_to_follow(l, limiting_domain)) and (not l in link_lst):
            link_lst.append(l)
    return link_lst


def make_words_set(title_desc):
    '''
    Make an index word list about a course.

    Inputs:
        title_desc: a string of title and description of a course

    Outputs:
        a set of index words about a course.
    '''
    words_set = set()
    title_desc = title_desc.lower().replace('%#160;', ' ')
    title_desc_lst = title_desc.split()
    for string in title_desc_lst:
        string = string.rstrip('!,.:')
        if string == '':
            continue
        if (string[0].isalpha()) and (not string in INDEX_IGNORE):
            words_set.add(string)
    return words_set


def make_words_dic(soup):
    '''
    Make an index dictionary per course on a web page.

    Inputs:
        soup: soup object.

    Outputs:
        an index word dictionary
    '''
    course_lst = soup.find_all('div', class_="courseblock main")
    words_dic = {}
    for course in course_lst:
        title = course.find('p', class_="courseblocktitle").text
        desc = course.find('p', class_="courseblockdesc").text
        if not util.find_sequence(course):
            course_code = title.split('.')[0].replace('.', '').replace("\xa0", " ")
            title_desc = title + ' ' + desc
            words_set = make_words_set(title_desc)
            words_dic[course_code] = words_set
        else:
            sub_course_lst = util.find_sequence(course)
            for sub_course in sub_course_lst:
                sub_title = sub_course.find('p', class_="courseblocktitle").text
                sub_desc = sub_course.find('p', class_="courseblockdesc").text
                course_code = sub_title.split('.')[0].replace('.', '').replace("\xa0", " ")
                title_desc = title  + ' ' + desc  + ' ' + sub_title  + ' ' +  sub_desc
                words_set = make_words_set(title_desc)
                words_dic[course_code] = words_set
    return words_dic


def go(num_pages_to_crawl, course_map_filename, index_filename):
    '''
    Crawl the college catalog and generates a CSV file with an index.

    Inputs:
        num_pages_to_crawl: the number of pages to process during the crawl
        course_map_filename: the name of a JSON file that contains the mapping
          course codes to course identifiers
        index_filename: the name for the CSV of the index.

    Outputs:
        CSV file of the index index.
    '''
    starting_url = ("http://www.classes.cs.uchicago.edu/archive/2015/winter"
                    "/12200-1/new.collegecatalog.uchicago.edu/index.html")
    limiting_domain = "classes.cs.uchicago.edu"

    whole_dic = {}
    link_q = queue.Queue()
    url = starting_url
    visit_link_set = set()
    num_pages = 0

    while num_pages < num_pages_to_crawl:
        request_ob_text, associated_url = get_html_text(url)
        if get_html_text(url) is None:
            url = link_q.get()
            continue
        visit_link_set.add(url)
        if url != associated_url:
            visit_link_set.add(associated_url)
        soup = bs4.BeautifulSoup(request_ob_text, 'html5lib')
        words_dic = make_words_dic(soup)
        whole_dic.update(words_dic)
        link_lst = get_link_lst(soup, url, limiting_domain)
        for link in link_lst:
            if not link in visit_link_set:
                link_q.put(link)
                visit_link_set.add(link)
        if link_q.empty():
            break
        url = link_q.get()
        num_pages += 1

    with open(course_map_filename) as f:
        course_map = json.load(f)
    with open(index_filename, 'w') as csvfile:
        w = csv.writer(csvfile, delimiter='|')
        for key, value in whole_dic.items():
            for word in value:
                w.writerow([course_map[key], word])


if __name__ == "__main__":
    usage = "python3 crawl.py <number of pages to crawl>"
    args_len = len(sys.argv)
    course_map_filename = "course_map.json"
    index_filename = "catalog_index.csv"
    if args_len == 1:
        num_pages_to_crawl = 1000
    elif args_len == 2:
        try:
            num_pages_to_crawl = int(sys.argv[1])
        except ValueError:
            print(usage)
            sys.exit(0)
    else:
        print(usage)
        sys.exit(0)

    go(num_pages_to_crawl, course_map_filename, index_filename)
