from bs4 import BeautifulSoup as bs
import requests
import csv
import re

def get_player_info(player_url, year):
    """Scrape player information from basketball-reference.com

    Given an individual player page on basketball-reference.com navigate the page
    to scrape pertinent information. This function may need updating with time
    as the html formatting of the player pages changes. A sample page for testing
    can be found at: http://www.basketball-reference.com/players/t/thomaku01.html

    Args:
        player_url: A string of the individual player page url (e.g. '/players/t/thomaku01.html')
            These can be found in the html table returned by the basketball-reference.com
            Player Season Finder tool.
        year: An integer year for the season of interest, corresponding to the
            the starting year of the season. For example, the 2016-17 season
            would be found using 2016.

    Returns:
        A list of the pertinent information. The information retrieved is the
        player's Position, Shooting Hand, Height, Weight, College, Draft Position,
        and Experience (in years). For example:
            ['PFC', 'Right', 6.75, 230.0, 'Texas Christian University', 10, 15]

    Sample Usage:
        >>> get_player_info('/players/t/thomaku01.html', 2010)
        ['PFC', 'Right', 6.75, 230.0, 'Texas Christian University', 10, 15]
    """
    # Construct the player page url, pull the text, and parse with BeautifulSoup.
    base_url = 'http://www.basketball-reference.com'
    url = base_url + player_url
    raw_text = requests.get(url).text
    soup = bs(raw_text, "lxml")

    # Find the html sections for the height and weight using specific tag attributes.
    feet = float(soup.find("span", {"itemprop" : "height"}).next_element.encode("utf-8")[0])
    inches = float(soup.find("span", {"itemprop" : "height"}).next_element.encode("utf-8")[2])
    ht = feet + inches / 12.0
    wt = float(soup.find("span", {"itemprop": "weight"}).next_element.encode("utf-8")[0:3])

    # Find remaining data by searching for particular text on the page.
    try:
        clg = str(soup.body.find(text = "\n  College:\n  ").next_element.next_element.text)
    except AttributeError:
        clg = "None"

    try:
        dft = int(re.sub('[^0-9]','',soup.body.find(text = "\n  Draft:\n  ").next_element.next_element.next_element.next_element.split(" ")[-3]))
    except AttributeError:
        dft = 61

    debut = soup.find(text = "NBA Debut: ").next_element.text.split(" ")
    debut_year = int(debut[-1])
    if str(debut[0]) in ["October", "November", "December"]:
        exp = year - debut_year
    else:
        exp = year - debut_year + 1

    try:
        hand = soup.body.find(text = "\n  Shoots:\n  ").next_element.encode("utf-8").strip()
    except AttributeError:
        hand = 'NA'

    try:
        positions = soup.body.find(text = "\n  Position:\n  ").next_element.encode("utf-8")[1:-7]
        pos = re.sub('[^A-Z]', '', positions)
    except AttributeError:
        pos = 'NA'

    # return constructed list.
    return([pos, hand, ht, wt, clg, dft, exp])

def get_player_stats(url_base, pagenum):
    """Scrape an individual page from the basketball-reference.com Player Season Finder.

    Scrape through the table on a page from the result of a Player Season Finder tool.
    This function can be used to iterate through the many pages of results and
    gather the data.

    Args:
        url_base: Url for the first page of the result from a search using the
            basketball-reference.com Player Season Finder (http://www.basketball-reference.com/play-index/psl_finder.cgi)
        pagenum: Integer page number of the search results. pagenum = 0 is the
            first page of the results, equivalent to url_base.

    Returns:
        list of lists. Each entry in the returned list in a list of the data for
        a player, i.e. data from each row in the table on each page of the search
        results as well as data from the player's individual page.

    Sample Usage:
        >>> data = get_player_stats(URL, 5)
    """
    # Transform the page number to the proper offset and construct the page url.
    id = 100*pagenum
    pages = '&offset='
    url = url_base + pages + str(id)

    # Send the request to the url for the html content, grab the text and parse it.
    raw_text = requests.get(url).text
    soup = bs(raw_text, "lxml")

    # Create empty lists.
    table = []
    title = []
    data = []

    # Iterate through the rows in the table.
    # If the row has attributes (i.e. class = 'thead') save the row to the title list.
    # Otherwise save it to the table list.
    for tr in soup.tbody.find_all('tr'):
        if len(tr.attrs):
            title.append(tr)
        else:
            table.append(tr)

    # If this is the first page of the search results construct the title row.
    if pagenum == 0:
        titleList = []
        for th in title[0].find_all('th')[1:]:
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

    # Iteratre through table rows and save the data to a list.
    for index, tr in enumerate(table):
        infoList = []
        player_url = tr.find("td", {"data-stat" : "player"}).next_element.get('href')
        tds = tr.find_all('td')
        year = int(tr.find("td", {"data-stat": "season"}).text.split("-")[0])
        for td in tds:
            infoList.append(td.text)

        [infoList.append(item) for item in get_player_info(player_url, year)]
        infoList.append(player_url)
        data.append(infoList)

    return(data)

def get_search_results(url, filename):
    """Gather results from search of basketball-reference.com Player Season Finder

    Iterate through the pages of a Player Season Finder search result and save
    the data for each page to a file. Each page data is gathered by calling
    the get_player_stats function.

    Args:
        url: url returned by Player Season Finder search.
        filename: name of CSV file to save data to.

    Returns:
        None. The function iterates through the pages of the search result until
        it encounters an AttributeError, the result of a page with no table on it.
        Each page is appended to the specified file
    """
    n = 0
    while True:
        print n
        try:
            data = get_player_stats(url, n)
            with open(filename, 'ab') as f:
                csv.writer(f).writerows(data)
            n += 1

        except AttributeError:
            break

if __name__ == '__main__':
    # URL = 'http://www.basketball-reference.com/play-index/psl_finder.cgi?request=1&match=single&type=advanced&per_minute_base=36&per_poss_base=100&lg_id=NBA&is_playoffs=N&year_min=2005&year_max=2016&franch_id=&season_start=1&season_end=-1&age_min=0&age_max=99&shoot_hand=&height_min=0&height_max=99&birth_country_is=Y&birth_country=&birth_state=&college_id=&draft_year=&is_active=&debut_yr_aba_start=&debut_yr_aba_end=&debut_yr_nba_start=&debut_yr_nba_end=&is_hof=&is_as=&as_comp=gt&as_val=&award=&pos_is_g=Y&pos_is_gf=Y&pos_is_f=Y&pos_is_fg=Y&pos_is_fc=Y&pos_is_c=Y&pos_is_cf=Y&qual=&c1stat=&c1comp=gt&c1val=&c2stat=&c2comp=gt&c2val=&c3stat=&c3comp=gt&c3val=&c4stat=&c4comp=gt&c4val=&c5stat=&c5comp=gt&c6mult=1.0&c6stat=&order_by=player&order_by_asc=Y'
    # URL = 'http://www.sports-reference.com/cbb/play-index/psl_finder.cgi?request=1&match=single&year_min=2010&year_max=&conf_id=&school_id=&class_is_fr=Y&class_is_so=Y&class_is_jr=Y&class_is_sr=Y&pos_is_g=Y&pos_is_gf=Y&pos_is_fg=Y&pos_is_f=Y&pos_is_fc=Y&pos_is_cf=Y&pos_is_c=Y&games_type=A&qual=&c1stat=&c1comp=&c1val=&c2stat=&c2comp=&c2val=&c3stat=&c3comp=&c3val=&c4stat=&c4comp=&c4val=&order_by=per&order_by_asc='
    URL = ("http://www.basketball-reference.com/play-index/psl_finder.cgi?request"
           "=1&match=single&type=advanced&per_minute_base=36&per_poss_base=100&lg"
           "_id=NBA&is_playoffs=N&year_min=2005&year_max=2016&franch_id=&season_"
           "start=1&season_end=-1&age_min=0&age_max=99&shoot_hand=&height_min=0&"
           "height_max=99&birth_country_is=Y&birth_country=&birth_state=&college"
           "_id=&draft_year=&is_active=&debut_yr_aba_start=&debut_yr_aba_end=&"
           "debut_yr_nba_start=&debut_yr_nba_end=&is_hof=&is_as=&as_comp=gt&"
           "as_val=&award=&pos_is_g=Y&pos_is_gf=Y&pos_is_f=Y&pos_is_fg=Y&pos_is_fc"
           "=Y&pos_is_c=Y&pos_is_cf=Y&qual=&c1stat=&c1comp=gt&c1val=&c2stat=&"
           "c2comp=gt&c2val=&c3stat=&c3comp=gt&c3val=&c4stat=&c4comp=gt&c4val=&"
           "c5stat=&c5comp=gt&c6mult=1.0&c6stat=&order_by=player&order_by_asc=Y"
           )
    get_search_results(URL, 'bbref_data_test.csv')
