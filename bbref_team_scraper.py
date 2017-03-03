from bs4 import BeautifulSoup as bs
import requests
import csv
import re

def convertStatSafe(stat):
    try:
        stat = float(stat)
        return(stat)
    except ValueError:
        return None

def astRatio(fga, fta, ast, tov):
    try:
        return (ast*100.0) / (fga + 0.44*fta + ast + tov)
    except TypeError:
        return None

def getCoach(soup):
    coachInfo = soup.body.find(text = "Coach:").next_element.next_element.text.split(" ")
    coachLast = str(' '.join(coachInfo[1:]))
    coachFirst = str(coachInfo[0])
    return((coachFirst, coachLast))

def getWL(soup):
    record = soup.body.find(text = "Record:").next_element.encode("utf-8").split(",")[0].split("-")
    wins = int(re.sub('[^0-9]', '', record[0]))
    losses = int(re.sub('[^0-9]', '', record[1]))
    return((wins, losses))

def getAstRt(soup):
    tbl = soup.find('table', {"id": "team_and_opponent"})
    data = tbl.find_all('tr', {'class': None})[0]
    tov = convertStatSafe(data.find('td', {'data-stat': 'tov'}).text)
    ast = convertStatSafe(data.find('td', {'data-stat': 'ast'}).text)
    fga = convertStatSafe(data.find('td', {'data-stat': 'fga'}).text)
    fta = convertStatSafe(data.find('td', {'data-stat': 'fta'}).text)
    astRt = astRatio(fga, fta, ast, tov)
    return(astRt)

def getTmAdvanced(soup):
    team_stats = (soup
                  .find('table', {'id': 'team_misc'})
                  .find_all('tr', {'class': None})[0])
    ortg = convertStatSafe(team_stats.find('td', {'data-stat': 'off_rtg'}).text)
    drtg = convertStatSafe(team_stats.find('td', {'data-stat': 'def_rtg'}).text)
    pace = convertStatSafe(team_stats.find('td', {'data-stat': 'pace'}).text)
    ftar = convertStatSafe(team_stats.find('td', {'data-stat': 'fta_per_fga_pct'}).text)
    fg3ar = convertStatSafe(team_stats.find('td', {'data-stat': 'fg3a_per_fga_pct'}).text)
    efgp = convertStatSafe(team_stats.find('td', {'data-stat': 'efg_pct'}).text)
    tovp = convertStatSafe(team_stats.find('td', {'data-stat': 'tov_pct'}).text)
    orbp = convertStatSafe(team_stats.find('td', {'data-stat': 'orb_pct'}).text)
    ftmr = convertStatSafe(team_stats.find('td', {'data-stat': 'ft_rate'}).text)
    oefgp = convertStatSafe(team_stats.find('td', {'data-stat': 'opp_efg_pct'}).text)
    otovp = convertStatSafe(team_stats.find('td', {'data-stat': 'opp_tov_pct'}).text)
    drbp = convertStatSafe(team_stats.find('td', {'data-stat': 'drb_pct'}).text)
    oftmr = convertStatSafe(team_stats.find('td', {'data-stat': 'opp_ft_rate'}).text)
    return([ortg, drtg, pace, ftar, fg3ar, efgp, tovp, orbp, ftmr, oefgp, otovp, drbp, oftmr])

def getTmBasic(soup, type = 'tot'):
    type_dict = {
        'tot': 0,
        'pg': 1,
        'rk': 2,
        'yoy': 3,
        'otot': 4,
        'opg': 5,
        'ork': 6,
        'oyoy': 7
    }
    type_code = type_dict[type]
    team_stats = (soup
                  .find('table', {'id': 'team_and_opponent'})
                  .find_all('tr', {'class': None})[type_code]
                  )
    g = convertStatSafe(team_stats.find('td', {'data-stat': 'g'}).text)
    mp = convertStatSafe(team_stats.find('td', {'data-stat': 'mp'}).text)
    fg = convertStatSafe(team_stats.find('td', {'data-stat': 'fg'}).text)
    fga = convertStatSafe(team_stats.find('td', {'data-stat': 'fga'}).text)
    fgp = convertStatSafe(team_stats.find('td', {'data-stat': 'fg_pct'}).text)
    fg3 = convertStatSafe(team_stats.find('td', {'data-stat': 'fg3'}).text)
    fg3a = convertStatSafe(team_stats.find('td', {'data-stat': 'fg3a'}).text)
    fg3p = convertStatSafe(team_stats.find('td', {'data-stat': 'fg3_pct'}).text)
    fg2 = convertStatSafe(team_stats.find('td', {'data-stat': 'fg2'}).text)
    fg2a = convertStatSafe(team_stats.find('td', {'data-stat': 'fg2a'}).text)
    fg2p = convertStatSafe(team_stats.find('td', {'data-stat': 'fg2_pct'}).text)
    ft = convertStatSafe(team_stats.find('td', {'data-stat': 'ft'}).text)
    fta = convertStatSafe(team_stats.find('td', {'data-stat': 'fta'}).text)
    ftp = convertStatSafe(team_stats.find('td', {'data-stat': 'ft_pct'}).text)
    orb = convertStatSafe(team_stats.find('td', {'data-stat': 'orb'}).text)
    drb = convertStatSafe(team_stats.find('td', {'data-stat': 'drb'}).text)
    trb = convertStatSafe(team_stats.find('td', {'data-stat': 'trb'}).text)
    ast = convertStatSafe(team_stats.find('td', {'data-stat': 'ast'}).text)
    stl = convertStatSafe(team_stats.find('td', {'data-stat': 'stl'}).text)
    blk = convertStatSafe(team_stats.find('td', {'data-stat': 'blk'}).text)
    tov = convertStatSafe(team_stats.find('td', {'data-stat': 'tov'}).text)
    pf = convertStatSafe(team_stats.find('td', {'data-stat': 'pf'}).text)
    pts = convertStatSafe(team_stats.find('td', {'data-stat': 'pts'}).text)
    dataList = [g, mp, fg, fga, fgp, fg3, fg3a, fg3p, fg2, fg2a, fg2p, ft, fta, ftp,
                orb, drb, trb, ast, stl, blk, tov, pf, pts]
    return(dataList)

def getTmInfo(tm, yr):
    url_base = "http://www.basketball-reference.com/teams/"
    if isinstance(yr, int):
        yr = str(yr)

    url = url_base + tm + "/" + yr + ".html"
    print url
    r = requests.get(url, allow_redirects=False)
    if r.status_code == requests.codes.ok:
        content = re.sub(r'(?m)^\<!--.*\n?', '', r.content)
        content = re.sub(r'(?m)^\-->.*\n?', '', content)
        soup = bs(content, 'lxml')
        box_data = getTmBasic(soup)
        astRt = getAstRt(soup)
        cf, cl = getCoach(soup)
        w, l = getWL(soup)
        adv_data = getTmAdvanced(soup)
        team_stats = soup.find('table', {'id': 'team_misc'}).find_all('tr', {'class': None})[0]
        mov = float(team_stats.find('td', {'data-stat': 'mov'}).text)
        sos = float(team_stats.find('td', {'data-stat': 'sos'}).text)
        srs = float(team_stats.find('td', {'data-stat': 'srs'}).text)
        arena = str(team_stats.find('td', {'data-stat': 'arena_name'}).text)
        attend_txt = team_stats.find('td', {'data-stat': 'attendance'}).text.split(',')
        attend = 0.0
        N_PLACES = len(attend_txt)
        for i, value in enumerate(attend_txt):
            power = N_PLACES - i - 1
            attend += float(value)*1000.0**power

        data = [tm, yr, cl, cf, w, l, mov, sos, srs, arena, attend] + box_data + adv_data + [astRt]
        # data = [tm, yr, astRt]
        return(data)
    else:
        return([])

# year = '2012'
# teams = ["ATL","BOS", "BRK","CHA", "CHO","CHI","CLE","DAL","DEN","DET","GSW","HOU","IND","LAC","LAL","MEM","MIA","MIL","MIN","NJN","NOH", "NOK", "NOP","NYK", "OKC", "ORL","PHI","PHO","POR","SAC","SAS","SEA","TOR","UTA","WAS"]
# # teams = ["CHO"]
# # getPlyrData("CHO", "2016")
# team_adv_data = []
# team_adv_data.append(["Team", "Year", "AstRt"])
# # team_adv_data.append(["Team", "Year", "Coach Lastname", "Coach Firstname", "W", "L", "MOV", "ORtg", "DRtg", "Pace", "FTAr", "3PAr", "eFGp", "TOVp", "ORBp", "FTMr", "oeFGp", "oTOVp", "DRBp", "oFTMr"])
# data = [['Team', 'Year', 'AstRt']]
# for y in range(2005, 2017):
#     year = str(y)
#     for team in teams:
#         info = getTmInfo(team, year)
#         if info:
#             team_adv_data.append(info)
# # print team_adv_data
# file = open("./tm_player_data/nba_team_data_05-16_astRt.csv", 'wb')
# csv.writer(file).writerows(team_adv_data)
#
# # url = "http://www.basketball-reference.com/teams/ATL/2016.html"
# url = "http://www.basketball-reference.com/teams/CHA/2012.html"
# raw_text = requests.get(url, allow_redirects=False).text
# soup = bs(raw_text)

# print getTblHeader(table)
if __name__ == '__main__':
    data = getTmInfo('BOS', '1950')
    # data = getTmInfo('CHI', '2010')
    print data
