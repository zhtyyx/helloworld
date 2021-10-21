import random
import re
from csv import writer

import requests
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData
from linkedin_jobs_scraper.filters import RelevanceFilters, TimeFilters, TypeFilters
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters


def on_data(data: EventData):
    with open('linkedinFile.csv', 'a+', newline='', encoding="utf-8") as write_obj:
        csv_writer = writer(write_obj)
        csv_writer.writerow((data.title, data.industries, data.apply_link, data.company, data.date,
                             data.link, data.description, data.employment_type,
                             data.job_function, data.job_index, data.location, data.place, data.query,
                             data.seniority_level))


class GatherProxy(object):
    '''To get proxy from http://gatherproxy.com/'''
    url = 'http://gatherproxy.com/proxylist'
    pre1 = re.compile(r'<tr.*?>(?:.|\n)*?</tr>')
    pre2 = re.compile(r"(?<=\(\').+?(?=\'\))")
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36"
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36"
        "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36"
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:22.0) Gecko/20130328 Firefox/22.0"
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1464.0 Safari/537.36"
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1623.0 Safari/537.36"
        "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36"
        "Mozilla/5.0 (X11; NetBSD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36"
        "Mozilla/5.0 (Windows NT 5.0; rv:21.0) Gecko/20100101 Firefox/21.0"
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36"
        "Opera/9.80 (Windows NT 5.1; U; cs) Presto/2.7.62 Version/11.01"
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36"
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20130331 Firefox/21.0"
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36"
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36"
        "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36"
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36"
        "Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/4E423F"
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36"
    ]
    header = {"user-agent": random.choice(user_agent_list)}

    def getelite(self, pages=1, uptime=70, fast=True):
        '''Get Elite Anomy proxy
        Pages define how many pages to get
        Uptime define the uptime(L/D)
        fast define only use fast proxy with short reponse time'''

        proxies = set()
        for i in range(1, pages + 1):
            params = {"Type": "elite", "PageIdx": str(i), "Uptime": str(uptime)}
            r = requests.post(self.url + "/anonymity/t=Elite", params=params, headers=self.header)
            for td in self.pre1.findall(r.text):
                if fast and 'center fast' not in td:
                    continue
                try:
                    tmp = self.pre2.findall(str(td))
                    if len(tmp) == 2:
                        proxies.add(tmp[0] + ":" + str(int('0x' + tmp[1], 16)))
                except:
                    pass
        return proxies


def on_error(error):
    print('[ON_ERROR]', error)


def on_end():
    print('[ON_END]')


gather_proxy = GatherProxy().getelite()

scraper = LinkedinScraper(
    chrome_executable_path=r'C:\Users\Hunter Zhang\PycharmProjects\py-linkedin-jobs-scraper\chromedriver.exe',
    chrome_options=None,  # You can pass your custom Chrome options here
    max_workers=1,  # How many threads will be spawn to run queries concurrently (one Chrome driver for each thread)
    slow_mo=5,  # Slow down the scraper to avoid 'Too many requests (429)' errors
    headless=True,  # Overrides headless mode only if chrome_options is None
    proxies=list(gather_proxy)
)

# Add event listeners
scraper.on(Events.DATA, on_data)
scraper.on(Events.ERROR, on_error)
scraper.on(Events.END, on_end)

queries = [
    Query(
        query='Healthcare Data Analyst',
        options=QueryOptions(
            locations=['United States'],
            optimize=True,
            limit=10000000000,
            filters=QueryFilters(
                # company_jobs_url="https://www.linkedin.com/jobs/search/?f_E=",  # Filter by companies
                relevance=RelevanceFilters.RELEVANT,
                time=TimeFilters.ANY,
                type=None,
                experience=None,
            )
        )
    ),
]

scraper.run(queries)
