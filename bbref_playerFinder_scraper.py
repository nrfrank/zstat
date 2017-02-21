from bs4 import BeautifulSoup as bs
import requests
import csv
import re

def unicode_check(c):
    if ord(c) <= 57:
        return(c)

def get_player_salary(player_url, year):
    home_url = 'http://www.basketball-reference.com'
    url = home_url + player_url
    raw_text = requests.get(url).text
    soup = bs(raw_text)

    try:
        table = soup.find_all('table', id = 'salaries')
        for tr in table[0].find_all('tr'):
            tds = tr.find_all('td')
            for i, td in enumerate(tds):
                if td.text == year:
                    return(tds[i+3].text)
    except IndexError:
        print 'No salary found'
        return('')

def get_player_info(player_url, year):
    home_url = 'http://www.basketball-reference.com'
    url = home_url + player_url
    raw_text = requests.get(url).text
    soup = bs(raw_text)

    ht = float(soup.body.find(text = "Height:").next_element.encode("utf-8")[1]) + float(soup.body.find(text = "Height:").next_element.encode("utf-8")[3])/12.0
    wt = float(soup.body.find(text = "Weight:").next_element.encode("utf-8")[1:4])

    try:
        clg = str(soup.body.find(text = "College:").next_element.next_element.text)
    except AttributeError:
        clg = "None"

    try:
        dft = int(re.sub('[^0-9]','',soup.body.find(text = "Draft:").next_element.next_element.next_element.next_element.split(" ")[-3]))
    except AttributeError:
        dft = 61

    debut = soup.body.find(text = "NBA Debut:").next_element.next_element.text.split(" ")
    debut_year = int(debut[-1])

    if str(debut[0]) in ["October", "November", "December"]:
        exp = year - debut_year
    else:
        exp = year - debut_year + 1

    try:
        hand = str(soup.body.find(text = "Shoots:").next_element.encode("utf-8")[1:])
    except AttributeError:
        hand = 'NA'

    try:
        positions = soup.body.find(text = "Position:").next_element.encode("utf-8")[1:-7]
        pos = re.sub('[^A-Z]', '', positions)
    except AttributeError:
        pos = 'NA'

    return([pos, hand, ht, wt, clg, dft, exp])

def get_player_exp(player_url, year):
    home_url = 'http://www.basketball-reference.com'

    url = home_url + player_url
    raw_text = requests.get(url).text
    soup = bs(raw_text)
    debut = soup.body.find(text = "NBA Debut:").next_element.next_element.text.split(" ")
    debut_year = int(debut[-1])

    if str(debut[0]) in ["October", "November", "December"]:
        exp = year - debut_year
    else:
        exp = year - debut_year + 1

    return(exp)

def get_player_stats(pagenum):
    id = 100*pagenum
    url_base = 'http://www.basketball-reference.com/play-index/psl_finder.cgi?request=1&match=single&type=advanced&per_minute_base=36&per_poss_base=100&lg_id=NBA&is_playoffs=N&year_min=2005&year_max=2016&franch_id=&season_start=1&season_end=-1&age_min=0&age_max=99&shoot_hand=&height_min=0&height_max=99&birth_country_is=Y&birth_country=&birth_state=&college_id=&draft_year=&is_active=&debut_yr_aba_start=&debut_yr_aba_end=&debut_yr_nba_start=&debut_yr_nba_end=&is_hof=&is_as=&as_comp=gt&as_val=&award=&pos_is_g=Y&pos_is_gf=Y&pos_is_f=Y&pos_is_fg=Y&pos_is_fc=Y&pos_is_c=Y&pos_is_cf=Y&qual=&c1stat=&c1comp=gt&c1val=&c2stat=&c2comp=gt&c2val=&c3stat=&c3comp=gt&c3val=&c4stat=&c4comp=gt&c4val=&c5stat=&c5comp=gt&c6mult=1.0&c6stat=&order_by=player&order_by_asc=Y'
    pages = '&offset='
    url = url_base + pages + str(id)
    raw_text = requests.get(url).text
    soup = bs(raw_text)

    table = []
    title = []
    data = []

    for tr in soup.tbody.find_all('tr'):
        if 'thead' not in tr.attrs['class']:
            table.append(tr)
        else:
            title.append(tr)

    if pagenum == 0:
        titleList = []
        for th in title[0].find_all('th'):
            titleList.append(th.text)

        titleList.append(u'Pos')
        titleList.append(u'Hand')
        titleList.append(u'Height')
        titleList.append(u'Weight')
        titleList.append(u'Clg')
        titleList.append(u'DraftRk')
        titleList.append(u'Exp')
        titleList.append(u'player_url')
        data.append(titleList)

    for index, tr in enumerate(table):
        infoList = []
        a = tr.find_all('a')
        player_url = a[0].get('href')
        tds = tr.find_all('td')
        year = int(tds[2].text.split("-")[0])
        for td in tds:
            infoList.append(td.text)

        [infoList.append(item) for item in get_player_info(player_url, year)]
        infoList.append(player_url)
        data.append(infoList)

    return(data)

# Set the number of entries in the search result and determine number of pages.
numPlayers = 5564
maxPage = numPlayers/100

# Loop through all the pages and save a csv file of the results for each.
for n in range(maxPage):
    data = get_player_stats(n)
    file = open('nba_player_data_05-16_page=' + str(n) + '.csv', 'wb')
    csv.writer(file).writerows(data)

# # Loop through all the pages and gather the full data set and save all at once.
# dataSet = [[] for x in range(maxPage)]
# dataSet = []
# for n in range(maxPage):
    # data = get_player_stats(n)
    # # Either method of accumulation works. Not sure which is faster.
    # dataSet[n] = data
    # dataSet.append(data)
# file = open('nba_player_data_05-16_all.csv', 'wb')
# csv.writer(file).writerows(dataSet)
