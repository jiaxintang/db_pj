import csv
import time
import json
import requests
from lxml import etree
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
# from pyvirtualdisplay import Display

from utils import *


confs_list = ['asplos', 'fast', 'hpca', 'isca', 'micro', 'sc', 'usenix', 'ppopp', 'mobicom', 'sigcomm', 'infocom',
              'ccs', 'crypto', 'eurocrypt', 'sp', 'uss', 'sigsoft', 'oopsla', 'icse', 'osdi', 'pldi', 'popl', 'sosp',
              'kbse', 'sigmod', 'kdd', 'sigir', 'vldb', 'icde', 'stoc', 'focs', 'lics', 'cav', 'mm', 'siggraph', 'vr',
              'aaai', 'cvpr', 'iccv', 'icml', 'ijcai', 'nips', 'acl', 'chi', 'huc', 'cscw', 'rtss', 'www']
year_list = ['2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018']

omit_list = [('uss', '2011'), ('cvpr', '2008'), ('icml', '2012'), ('acl', '2016'), ('aaai', '2010'), ('aaai', '2011'),
             ('aaai', '2012'), ('aaai', '2013'), ('sc', '2009'), ('usenix', '2009'), ('usenix', '2011'), ('usenix', '2010')]


def get_proceedings_url(driver, conf):
    conf_dict = {}
    try:
        header = driver.find_element_by_xpath("//div[@id='main']/header[1]")
    except Exception as e:
        print e
        return "None"
    conf_name = header.text
    print conf_name, '(' + conf + ')'

    i = 1
    flag = False
    while True:
        i += 1
        try:
            flag = False
            this_conf = driver.find_element_by_xpath("//div[@id='main']/header[" + str(i) + "]").text
            # print this_conf
            this_year = ''
            for year in year_list:
                if year in this_conf:
                    this_year = year
                    break
            if this_year == '':
                continue
            flag = True
            temp = driver.find_elements_by_xpath("//div[@id='main']/header[" + str(i) + "]/following-sibling::*[1]")[0]
            if temp.tag_name == 'p':
                p = 2
            else:
                p = 1
            # print temp.tag_name
            contents = driver.find_elements_by_xpath("//div[@id='main']/header[" + str(i) + "]/following-sibling::*[" + str(p) + "]/li/div[@class='data']/span[@class='title']")
            content = contents[0].text
            # print content
            url = driver.find_elements_by_xpath("//div[@id='main']/header[" + str(i) + "]/following-sibling::*[" + str(p) + "]/li/div[@class='data']/a[@class='toc-link']")[0].get_attribute('href')
            conf_dict[this_year] = url
            flag = False
        except Exception as e:
            # print e
            if flag:
                continue
            else:
                break
    print conf_dict
    return conf_dict

def get_paper(driver, page_flag):
    paper_list = []
    s = 0

    html = etree.HTML(driver.page_source)
    session = html.xpath("//div[@id='main']/header")

    if len(session) < 2:
        tags = html.xpath("//li[@class='entry inproceedings']/div[@class='data']")
        # flag = False
        for tag in tags:
            author_list = []
            if page_flag:
                try:
                    page = tag.xpath(".//span[@itemprop='pagination']")[0].text
                    if '-' in page:
                        begin = page.split('-')[0]
                        end = page.split('-')[1]
                        if ':' in begin:
                            begin = begin.split(':')[1]
                            print 'page contain : '
                        if ':' in end: end = end.split(':')[1]
                        begin = (int)(begin)
                        end = (int)(end)
                        pages = end - begin + 1
                    else:
                        pages = 1
                except Exception as e:
                    print "Page error!", e
                    continue
            else:
                pages = -1
            authors = tag.xpath(".//span[@itemprop='author']/a")
            for author in authors:
                author_url = author.get('href')
                author_name = author.xpath(".//span[@itemprop='name']")[0]
                author_list.append(author_name.text + '.....' + author_url)
            title = tag.xpath(".//span[@class='title']")[0].text
            temp_dict = {}
            temp_dict['author'] = author_list
            temp_dict['page'] = pages
            temp_dict['title'] = title
            paper_list.append(temp_dict)
        return paper_list

    idx = 1
    flag = False
    while True:
        idx += 1
        try:
            flag = False
            title_flag = False
            try:
                session = html.xpath("//div[@id='main']/header[" + str(idx) + "]/h2")[0].text
                title_flag = True
            except Exception as e:
                print 'header2', e
            if not title_flag:
                try:
                    session = html.xpath("//div[@id='main']/header[" + str(idx) + "]/h3")[0].text
                    title_flag = True
                except Exception as e:
                    print 'header3', e
                    print
            if title_flag:
                flag = True
            else:
                assert(1==0)
            flag = True
            if 'Poster' in session or 'poster' in session:
                continue
            contents = html.xpath("//div[@id='main']/header[" + str(idx) + "]/following-sibling::*[1]")[0]
            tags = contents.xpath(".//li[@class='entry inproceedings']/div[@class='data']")
            for tag in tags:
                author_list = []
                if page_flag:
                    try:
                        page = tag.xpath(".//span[@itemprop='pagination']")[0].text
                        if '-' in page:
                            begin = page.split('-')[0]
                            end = page.split('-')[1]
                            if ':' in begin:
                                begin = begin.split(':')[1]
                                print 'page contain : '
                            if ':' in end: end = end.split(':')[1]
                            begin = (int)(begin)
                            end = (int)(end)
                            pages = end - begin + 1
                        else:
                            pages = 1
                        if pages <= 3: continue
                    except Exception as e:
                        print "Page error!", e
                        continue
                else:
                    pages = -1
                authors = tag.xpath(".//span[@itemprop='author']/a")
                for author in authors:
                    author_url = author.get('href')
                    author_name = author.xpath(".//span[@itemprop='name']")[0]
                    author_list.append(author_name.text + '.....' + author_url)
                title = tag.xpath(".//span[@class='title']")[0].text
                temp_dict = {}
                temp_dict['author'] = author_list
                temp_dict['page'] = pages
                temp_dict['title'] = title
                paper_list.append(temp_dict)
        except Exception as e:
            # print e
            # print flag
            if flag:
                continue
            else:
                break
    # print paper_list
    return paper_list






if __name__ == '__main__':
    driver = initial()
    result_dict = {}
    sum = 0
    for conf in confs_list:
        driver.get('http://dblp.org/db/conf/' + conf)
        conf_dict = get_proceedings_url(driver, conf)
        result_dict[conf] = {}
        print conf_dict
        for year in conf_dict.keys():
            print year
            url = conf_dict[year]
            driver.get(url)
            if (conf, year) not in omit_list:
                paper_list = get_paper(driver, True)
            else:
                paper_list = get_paper(driver, False)
            result_dict[conf][year] = paper_list
            sum += len(paper_list)
    with open('result.json', 'w') as f:
        f.write(json.dumps(result_dict))
    f.close()
    print sum
    # temp_confs = ['pldi', 'sigir', 'vldb', 'icde', 'siggraph']
    # temp_confs = ['icde']
    # for conf in temp_confs:
    #     driver.get('http://dblp.org/db/conf/' + conf)
    #     conf_dict = get_proceedings_url(driver, conf)

    # with open('result.json', 'r') as fp:
    #     result_dict = json.loads(fp.read())
    # fp.close()
    # for conf in confs_list:
    #     for year in result_dict[conf].keys():
    #         sum += len(result_dict[conf][year])
    # print sum
