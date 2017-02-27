"""
DISCLAIMER:
This crawler is only for educational purposes. It is part of a project with the topic 'Crowdfunding.' It is by no means
intended for illegal use whatsoever.
It doesn't work perfectly, but it's fine for now. It may break at times.
And the produced SQL queries may need very little manual corrections
"""
import random
from datetime import date, timedelta

import requests
from bs4 import BeautifulSoup

home_page = 'https://www.kickstarter.com/discover/popular?ref=discover_index'
base_url = 'https://www.kickstarter.com'

# CSS selectors
project_link_elem = 'li.project .project-thumbnail-wrap'
img_elem = '#video-section img'
title_elem = 'h2.type-24.type-28-sm.type-38-md.navy-700.medium.mb3'
description_elem = 'p.type-14.type-18-md.navy-600.mb0'
target_fund_elem = '.block.navy-600.type-12.type-14-md.lh3-lg span.money'

# Start date: NOW()
# End date: NOW() + TRUNC((RANDOM() * 60) + 30)


def download_page(url):
    res = requests.get(url)
    while res.status_code != 200:
        res = requests.get(url)
    return res.text


def get_href_list(link_elems):
    return [link_elem.get('href') for link_elem in link_elems]


def sanitize_sql(param):
    sanitized = param.replace('\'', '\'\'')
    return sanitized


def get_projects(hrefs):
    projects = []
    count = 0
    for href in hrefs:
        if 'https' not in href:
            href = base_url + href
        html = download_page(href)
        soup = BeautifulSoup(html, 'html.parser')
        photo_url = soup.select(img_elem)[0].get('src')
        title = soup.select(title_elem)[0].string.strip()
        description = soup.select(description_elem)[0].string.strip()
        target_fund = soup.select(target_fund_elem)[0].string[1:].strip().replace(',', '')
        project = {
            'photo_url': sanitize_sql(photo_url),
            'title': sanitize_sql(title),
            'description': sanitize_sql(description),
            'target_fund': sanitize_sql(target_fund)
        }
        projects.append(project)
        print(count)
        if count == 100:
            break
        count += 1
    return projects

if __name__ == '__main__':
    html = download_page(home_page)
    soup = BeautifulSoup(html, 'html.parser')
    link_elems = soup.select(project_link_elem)
    hrefs = get_href_list(link_elems)

    projects = get_projects(hrefs)
    today_date = date.today()
    sqls = []
    sql = 'INSERT INTO projects (title, description, start_date, end_date, target_fund, photo_url) ' \
          'VALUES (\'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\');\n'
    count = 0
    for project in projects:
        random_time_delta = timedelta(days=random.randint(30, 90))  # 1-3 months
        end_date = today_date + random_time_delta
        print(count)
        sqls.append(sql.format(
            project['title'].encode('utf-8'),
            project['description'].encode('utf-8'),
            unicode(today_date),
            unicode(end_date),
            project['target_fund'],
            project['photo_url']
        ))
        count += 1

    with open('projects.sql', 'w') as f:
        f.writelines(sqls)