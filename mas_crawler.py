# -*- coding:utf-8 -*-

from selenium import webdriver
import time
from utils import *
from lxml import etree
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

count = -1
url_ = 'https://academic.microsoft.com/#/search?iq=%40abcdefg%40&q=abcdefg&filters=&from=0&sort=0'


def get_abstract(html):
    tag = html.xpath("//span[@data-bind='html: abstract']")
    try:
        return tag[0].text
    except Exception as e:
        return None


def get_author_departments(html):
    departments = []
    try:
        tags = html.xpath(
            "//paper-tile//article[1]//ul[@class='ulist-content']//span[@class='affiliation']//li//a[@class='button-link']")
        # print len(tags)
        for tag in tags:
            departments.append(tag.text.strip())
        tags = html.xpath("//paper-tile//article[1]//ul[@class='ulist-content']//span[@class='affiliation']//li//span")
        for tag in tags:
            departments.append(tag.text.strip())
        return departments
    except Exception as e:
        return None


def get_citation(html):
    try:
        tag = html.xpath("//paper-tile//article[1]//span[@class='c-count']")
        if len(tag) == 0:
            tag = html.xpath("//paper-tile//article[1]//section[@class='paper-actions']//ul[@class='action-links-horizontal']//li/a/span")
        return tag[0].text
    except Exception as e:
        print 'citation wrong'
        return None



def crawl_mas(driver, text, dst):
    driver.find_elements_by_xpath("//body[@id='isrcWrapper']//div[@class='search-input']/input")[0].clear()
    driver.find_elements_by_xpath("//body[@id='isrcWrapper']//div[@class='search-input']/input")[0].send_keys(text)
    time.sleep(5)
    driver.find_elements_by_xpath("//body[@id='isrcWrapper']//span[@class='ma-sem-search']")[0].click()
    time.sleep(10)
    with open(dst, "w") as fp:
        fp.write(driver.page_source)
    fp.close()
    html = etree.HTML(driver.page_source)
    departments = get_author_departments(html)
    abstract = get_abstract(html)
    citation = get_citation(html)
    if (not departments) and (not abstract) and (not citation):
        return False, {}
    paper = {}
    paper['departments'] = departments
    paper['abstract'] = abstract
    paper['citation'] = citation
    print paper
    return True, paper

def scrape_all(conf_dict, origin):
    driver = initial()
    driver.get(url_)
    print 'Begin'
    global count
    mas_dict = {}
    for (conf, dicts) in conf_dict.items():
        print conf
        for (year, titles) in conf_dict[conf].items():
            # mas_dict = {}
            for paper in titles:
                count += 1
                if count < origin:
                    continue
                print paper
                try:
                    title = paper['title']
                    print generate_file_name(conf, year, str(hash(title))) + '.html'
                    flag, paper_dict = crawl_mas(driver, title, (os.path.join("mas_result", generate_file_name(conf, year, str(hash(title)))) + '.html'))
                    if not flag:
                        raise Exception("Not valid data")
                    # mas_dict[title] = paper_dict
                    with open(os.path.join("mas_json", generate_file_name(conf, year, str(hash(title)))) + '.json', 'w') as f:
                        f.write(json.dumps(paper_dict))
                    f.close()
                    print count
                except Exception as e:
                    print e


            # print conf + ' ' + year,  count

                # time.sleep(6)

if __name__ == '__main__':
    # text = 'Camel: Content-Aware and Meta-path Augmented Metric Learning for Author Identification'
    with open('origin', 'r') as fp:
        origin = (int)(fp.read())
    fp.close()
    with open('./result.json', 'r') as fp:
        conf_dict = json.loads(fp.read())
    fp.close()
    scrape_all(conf_dict, origin)
