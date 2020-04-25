import urllib.request
from bs4 import BeautifulSoup
import re
import csv
import time
import datetime

active_listings = []

#############################    NOTES    #############################

# item number of listings increments down by 1 every new listing -- weird

# HAS A 5 MINUTE SNIPE TIMER. If ends at 10PM, and a bid is placed between 9:55-10, extended by 5 mins

#############################    NOTES    #############################


# --------- grab number of pages --------------- #
def get_number_of_pages():
    url = "https://www.lsoauctions.com/category.cfm?sellerid=867362294&catid=867362294&listing=going&startrow=1"
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

        url = "https://www.lsoauctions.com/category.cfm?sellerid=867362294&catid=867362294&listing=going&startrow=" + str(rownum)
        print(url)
        # download URl and extract the content to variable html
        request = urllib.request.Request(url)  # send request to site
        html = urllib.request.urlopen(request).read()  # open URL and download HTML content
        soup = BeautifulSoup(html, 'html.parser')

        process_page_html(soup)
        time.sleep(5)
        page += 1

    print(active_listings)
    print('number of listings found:', len(active_listings))
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

    text = text.split(' , ')
    listings = []

    for item in text:
        start = ' - '
        end = ' CT'
        item = str(item[item.find(start)+len(start):item.rfind(end)])
        listings.append(item)

    clean_listings = []

    for item in listings:
        item = item.replace('  ', '')
        item = item.split('\t')
        clean_listings.append(item)

    # FORMAT: [[listing name, price, bids, date end], [...]]
    # print(clean_listings)

    links = []
    # USE THIS TO GET ITEMNUM FROM POSTINGS AND CREATE LINK (https://www.lsoauctions.com/ + details.cfm?itemnum=1074476)
    for item in main_table.find_all("a", class_="item-list-title"):
        holder = 'https://www.lsoauctions.com/' + item.get('href')
        links.append(holder)

    # FORMAT: [link1, link2, ..]
    # print(links)

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


# this runs the program
get_number_of_pages()


# ----------- check against my keywords ------------- #
send_keyword = []
send_cheap = []
send_high_priority = []

# ----------------- Bans words ----------------------- #
banwords = ['chair', 'stool', 'bike', 'chevy']

for item in active_listings:
    for word in banwords:
        if word in item[0].lower():
            # print('banned: ', item, ' because of word: ', word)
            active_listings.remove(item)

print('\n\n\n\n\n')

#for item in active_listings:
#    if item[1] < 50:
#        pass
        # send an alert

# ----------------- finds time left ----------------------- #
print(active_listings)
############################################### LEFT OFF HERE, NEED TO FIGURE OUT ERROR I'M GETTING
for item in active_listings:
    print(item[3])
    date = item[3]
    date2 = '18/' + date
    objdate = datetime.datetime.strptime(date2, '%y/%m/%d %I:%M %p')

    today = datetime.datetime.now()
    today = today.replace(microsecond=0)

    time_left = abs(objdate - today)

    item.append(time_left)


print('active: ', active_listings)
    #   send_price.append(item)

    #if item in keywords:
    #   send_keyword.append(item)


## Checks if there are items that spring multiple good signs. send these first
#for item in send_keyword:
#   if item in send_cheap:
    #   send_high_priority.append(item)

# ----------- send alerts ------------- #
'''
while i < len(newspapers):
    while j < len(keywords):
        items = []
        actionword = newspapers[i] + keywords[j] + '.csv'
        with open(actionword) as File:
            reader = csv.reader(File,
                                quoting=csv.QUOTE_MINIMAL)
            for row in reader:
                items.append(row)
        items.pop(0)
        found_count = (len(items))

        x = 0
        y = 0
        message = ''
        while x < len(items):
            message = message + items[x][0] + items[x][1] + '\n'        ##### LEFT OFF HERE. OUTPUTTING keyword many times -- try using append()
            x += 1

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("pythonsendert@gmail.com", "G1gemAirbus")

        hold = '\n' + 'StorageScraper found the following keyword:' + '\n\n' + keywords[j] + '    ' + str(found_count) + ' times' + '\n\n' + 'in:' + '\n\n' + newspapers[i] + '\n\n' + 'SUMMARY:\n\n' + message
        msg = hold.encode("utf-8")
        print(msg)
        server.sendmail("pyhtonsendert@gmail.com", "", msg)
        j += 1
    i += 1
    j = 0
'''

# ------------ create schedule of times to bid ---------- #


# --------------- auto bid feature ------------------ #







