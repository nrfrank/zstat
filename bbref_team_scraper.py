from bs4 import BeautifulSoup as bs
import requests
import csv
import re

def astRatio(fga, fta, ast, tov):
    return (ast*100.0) / (fga + 0.44*fta + ast + tov)

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

def getCoach(soup):
    coachInfo = soup.body.find(text = "Coach:").next_element.next_element.text.split(" ")
    coachLast = str(coachInfo[1])
    coachFirst = str(coachInfo[0])
    return((coachFirst, coachLast))

def getWL(soup):
    record = soup.body.find(text = "Record:").next_element.encode("utf-8").split(",")[0].split("-")
    wins = int(re.sub('[^0-9]', '', record[0]))
    losses = int(re.sub('[^0-9]', '', record[1]))
    return((wins, losses))

def getTblHeader(tbl, rmEmpty = True):
    if rmEmpty:
        return([str(h.text) for h in tbl.findAll('th') if len(h) > 0])
    else:
        return([str(h.text) for h in tbl.findAll('th')])

def getTblRowData(row, rmEmpty = True):
    if rmEmpty:
        return([str(d.text) for d in row.findAll('td') if len(d) > 0])
    else:
        return([str(d.text) for d in row.findAll('td')])

def getAstRt(soup):
    tbl = soup.find('table', id="team_stats")
    data = getTblRowData(tbl.tbody.findAll('tr')[0], rmEmpty = False)
    ast = float(data[18])
    tov = float(data[21])
    fga = float(data[4])
    fta = float(data[13])
    astRt = astRatio(fga, fta, ast, tov)
    return(astRt)

def getPlyrTotData(soup):
    data = []
    totsTable = soup.find('table', id = 'totals')
    totsHeader = getTblHeader(totsTable)
    data.append(totsHeader)
    for row in totsTable.tbody.findAll('tr'):
        data.append(getTblRowData(row, rmEmpty = False))
    return(data)

def getPlyrAdvData(soup, year):
    if type(year) == type(str()):
        year = int(year)
    data = []
    advTable = soup.find('table', id = 'advanced')
    advHeader = getTblHeader(advTable)
    infoHeader = ["Pos", "Hand", "HT", "WT", "CLG", "DFT", "EXP"]
    data.append(advHeader + infoHeader)
    for row in advTable.tbody.findAll('tr'):
        plyr_url = row.findAll('a')[0].get('href')
        data.append(getTblRowData(row) + get_player_info(plyr_url, year))
    return(data)

def getTmInfo(tm, yr):
    url_base = "http://www.basketball-reference.com/teams/"
    url = url_base + tm + "/" + yr + ".html"
    print url
    raw_text = requests.get(url).text
    r = requests.get(url, allow_redirects=False)
    if r.status_code != 301:
        soup = bs(r.text)
        astRt = getAstRt(soup)
        # cf, cl = getCoach(soup)
        # w, l = getWL(soup)
        # team_stats = soup.find('table', id='team_misc').tbody.findAll('tr')[0].findAll('td')
        # mov = float(team_stats[3].text)
        # adv_stats = [float(s.text) for s in team_stats[6:19]]
        # data = [tm, yr, cl, cf, w, l, mov] + adv_stats
        data = [tm, yr, astRt]
        return(data)
    else:
        return([])

def getPlyrData(tm, yr):
    url_base = "http://www.basketball-reference.com/teams/"
    url = url_base + tm + "/" + yr + ".html"
    print url
    r = requests.get(url, allow_redirects=False)
    if r.status_code != 301:
        soup = bs(r.text)
        # coach = getCoach(soup)
        file = open("./tm_player_data/" + tm + "_" + yr + "_plyr-adv.csv", 'wb')
        csv.writer(file).writerows(getPlyrAdvData(soup, yr))
        # file = open("./tm_player_data/" + tm + "_" + yr + "_plyr-tot.csv", 'wb')
        # csv.writer(file).writerows(getPlyrTotData(soup))

# year = '2012'
teams = ["ATL","BOS", "BRK","CHA", "CHO","CHI","CLE","DAL","DEN","DET","GSW","HOU","IND","LAC","LAL","MEM","MIA","MIL","MIN","NJN","NOH", "NOK", "NOP","NYK", "OKC", "ORL","PHI","PHO","POR","SAC","SAS","SEA","TOR","UTA","WAS"]
# teams = ["CHO"]
# getPlyrData("CHO", "2016")
team_adv_data = []
team_adv_data.append(["Team", "Year", "AstRt"])
# team_adv_data.append(["Team", "Year", "Coach Lastname", "Coach Firstname", "W", "L", "MOV", "ORtg", "DRtg", "Pace", "FTAr", "3PAr", "eFGp", "TOVp", "ORBp", "FTMr", "oeFGp", "oTOVp", "DRBp", "oFTMr"])
data = [['Team', 'Year', 'AstRt']]
for y in range(2005, 2017):
    year = str(y)
    for team in teams:
        # getPlyrData(team, year)
        info = getTmInfo(team, year)
        if info:
            team_adv_data.append(info)
# print team_adv_data
file = open("./tm_player_data/nba_team_data_05-16_astRt.csv", 'wb')
csv.writer(file).writerows(team_adv_data)

# url = "http://www.basketball-reference.com/teams/ATL/2016.html"
url = "http://www.basketball-reference.com/teams/CHA/2012.html"
raw_text = requests.get(url, allow_redirects=False).text
soup = bs(raw_text)

# print getTblHeader(table)
