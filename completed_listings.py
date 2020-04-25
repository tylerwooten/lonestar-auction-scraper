import urllib.request
from bs4 import BeautifulSoup
import re
import csv
import time

active_listings = []
link_holder = []
# NEW FEATURE TO ADD #
# Save old auctions to csv based off of itemnum so I can see what items have gone for before #


#############################    NOTES    #############################

# HAS A 5 MINUTE SNIPE TIMER. If ends at 10PM, and a bid is placed between 9:55-10, extended by 5 mins

#############################    NOTES    #############################


# --------- grab number of pages --------------- #
def get_number_of_pages():
    url = "https://www.lsoauctions.com/category.cfm?sortby=date_desc&sellerid=867362294&catid=867362294&listing=completed&startrow=1"
    # download URl and extract the content to variable html
    request = urllib.request.Request(url)  # send request to site
    html = urllib.request.urlopen(request).read()  # open URL and download HTML content
    soup = BeautifulSoup(html, 'html.parser')

    page_numbers = soup.find(lambda tag: tag.name == 'table' and tag.has_attr('width') and tag['width'] == "97%")
    pages = page_numbers.find_all("a", class_="item-list-page-link")
    page_max = len(pages) + 1  # + 1 to include the page we are on already
    print('Number of pages: ', page_max)

    get_page_soup(page_max)
    return


# --------- grab page soup --------------- #
def get_page_soup(page_max):
    #print('running', 'getpagesoup')
    time.sleep(5)
    page = 0  # indexing starts at 0 :)
    while page < page_max:
        rownum = (int(page) * 30) + 1

        url = "https://www.lsoauctions.com/category.cfm?sortby=date_desc&sellerid=867362294&catid=867362294&listing=completed&startrow=" + str(rownum)
        print(url)
        # download URl and extract the content to variable html
        request = urllib.request.Request(url)  # send request to site
        html = urllib.request.urlopen(request).read()  # open URL and download HTML content
        soup = BeautifulSoup(html, 'html.parser')

        process_page_html(soup)
        time.sleep(5)
        page += 1

    # write_to_csv()
    return active_listings


# -------------- pass the HTML to BeautifulSoup ---------------#
def process_page_html(soup):
    #print('running', 'process_page_html')

    # get HTML of table on page
    main_table = soup.find(lambda tag: tag.name == 'table' and tag.has_attr('width') and tag['width'] == "98%")
    # find all items in tr tags with class item-list-row
    rows = main_table.find_all("tr", class_="item-list-row")
    cleanrows = BeautifulSoup(str(rows), 'html.parser')

    parse_html(main_table, cleanrows)
    return


# -------- parse data ---------- #
def parse_html(main_table, cleanrows):
    #print('running', 'parse_html')
    text = cleanrows.get_text()
    text = text.replace('      ', '')
    text = text.replace('                           ', '')
    text = text.replace('TEXAS A&M; UNIVERSITY - College Station', '')
    text = text.replace('\n', '')
    text = text.replace('[', '')
    text = text.replace(']', '')
    text = text.replace('COMPLETED', '\t')

    #print(text)
    text = text.split(',  ')
    listings = []

    for item in text:
        start = ' - '
        end = ' CT'
        item = str(item[item.find(start)+len(start):item.rfind(end)])
        listings.append(item)

    clean_listings = []
    #print(listings)
    for item in listings:
        item = item.replace('  ', '')
        item = item.split('\t')
        clean_listings.append(item)

    # FORMAT: [[listing name, price, bids, date end], [...]]
    #print(clean_listings)

    links = []
    # USE THIS TO GET ITEMNUM FROM POSTINGS AND CREATE LINK (https://www.lsoauctions.com/ + details.cfm?itemnum=1074476)
    for item in main_table.find_all("a", class_="item-list-title"):
        holder = 'https://www.lsoauctions.com/' + item.get('href')
        links.append(holder)

    # FORMAT: [link1, link2, ..]
    # print(links)
    link_holder.append(links)

    concat_links_and_data(clean_listings, links)
    return


# --------- combine clean_listings and links --------------- #
def concat_links_and_data(clean_listings, links):
    #print('running', 'concat_links_and_data')
    page_data = []
    i = 0

    while i < len(links):
        for item in clean_listings:
            item.append(links[i])
            page_data.append(item)
            i += 1

        # print(page_data)

    # FORMAT: [[listing name, price, bids, date end, link], [...]]
    for item in page_data:
        active_listings.append(item)

    return

get_number_of_pages()


print(active_listings)
print('\n\n\nnumber of listings found:', len(active_listings))

# ----------- save to csv ------------- #
x = []
with open('completed_listings.csv', 'r', newline='') as csv_file:

    reader = csv.reader(csv_file)

    for header in reader:
        x.append(header[4])  # uses links to see if this item is already in my database

new_counter = 0
dup_counter = 0

with open('completed_listings.csv', 'a', newline='') as csv_file:

    writer = csv.writer(csv_file)
    writer.writerow(['Title', 'Price', 'Bids', 'Finish Time', 'Url'])

    for item in active_listings:
        if item[4] in x:
            dup_counter += 1
        else:
            writer.writerow(item)
            new_counter += 1

print('number of duplicates: ', dup_counter)
print('number of items added: ', new_counter)



