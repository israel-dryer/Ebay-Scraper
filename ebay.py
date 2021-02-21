"""
    Perform a simple Ebay searcha and extract the results to a CSV file
    Author : Israel Dryer
    Modified : 2021-02-21
    
"""
import csv
import requests
from lxml import html


def get_page_items(tree):
    container = tree.xpath("//ul[contains(@class, 'srp-results')]")
    if container:
        return container[0].xpath(".//li[contains(@class, 's-item')]")
    else:
        return []


def create_search_record(item):
    title = "".join(item.xpath(".//h3/text()"))
    sub_title = "".join(item.xpath(".//div[@class='s-item__subtitle']/text()"))
    sub_title += " " + \
        "".join(item.xpath(
            ".//div[@class='s-item__subtitle']//span[@class='SECONDARY_INFO']/text()"))
    rating = "".join(item.xpath(
        ".//div[@class='x-star-rating']//span[@class='clipped']/text()"))
    item_price = "".join(item.xpath(".//span[@class='s-item__price']/text()"))
    trending_price = "".join(item.xpath(
        ".//span[@class='s-item__trending-price']/span[@class='STRIKETHROUGH']/text()"))
    item_link = "".join(item.xpath(".//a[@class='s-item__link']/@href"))
    return (title, sub_title, rating, item_price, trending_price, item_link)


def get_next_page(tree):
    return "".join(tree.xpath("//a[@class='pagination__next']/@href"))


def search_ebay(keywords):
    url = "https://www.ebay.com/sch/i.html?&_nkw=" + keywords.replace(" ", "+")
    response = requests.get(url)

    # get first page
    etree = html.fromstring(response.text)
    page_data = []

    # get remaining pages if existing
    while True:
        items = get_page_items(etree)
        if not items:
            break

        for item in items:
            page_data.append(create_search_record(item))

        next_page = get_next_page(etree)
        if not next_page:
            break

        response = requests.get(next_page)
        if response.status_code != 200:
            break

        etree = html.fromstring(response.text)

    return page_data


def save_results(records, filename, save_method='w'):
    with open(filename, save_method, newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Title', 'SubTitle', 'Rating',
                         'ItemPrice', 'TrendingPrice', 'ItemLink'])
        writer.writerows(records)


if __name__ == '__main__':

    results = search_ebay('curved monitor')

    if results:
        save_results(results, 'curved_monitor.csv')
