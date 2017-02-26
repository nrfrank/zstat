# UNC ZStat Code for Tutorials

This repository will serve as a code base for UNC's ZStat Sport Analytics Working Group. The purpose is to provide some sample functions as a starting point for tutorials and for group development. Code samples will be added and documented with time, but will largely focus on methods for obtaining (web scraping) and cleaning (tidying) data as well as some analysis and visualization.

> Please note, while I will ensure that all code added to this repository is functional upon commit, I will not be fastidiously monitoring it. As such, changes to required packages or the websites the code is pulling from may break some methods. Nevertheless, it should be a good starting point.

## Getting Started

You can obtain all the code in this repository by forking it from your own GitHub account or simply opening the files and copying/pasting the content into your favorite texy editor or IDE.

### Prerequisites

This code uses Python 2.7.x. You can download base [Python](https://www.python.org/) individually or as part of any number of [distributions](https://wiki.python.org/moin/PythonDistributions) (e.g. [Anaconda](https://www.continuum.io/downloads) or [Canopy](https://www.enthought.com/products/canopy/))

Two additional libraries are also required, namely [Requests](http://docs.python-requests.org/en/master/) and [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#). Both can be obtained using [pip](https://pypi.python.org/pypi/pip), the currently recommended tool for installing Python packages. It is included by default in Python versions 2.7.9 and later.

```
pip install beautifulsoup4
pip install requests
```

## Usage

Below you will find some basic information and working examples.

### basketball-reference.com Player Season Finder Scraper

The code in `bbref_playerFinder_scraper.py` can be used to scrape the results from a search using the [Basketball Reference
Player Season Finder Tool](http://www.basketball-reference.com/play-index/psl_finder.cgi). The main function of interest is `get_search_results(url, filename)`. This will take a url returned by the Player Season Finder tool and the name of the file you wish to save the data to (full file path) and will scrape the entire search result. It will also grab some additional data from each player's basketball-reference.com profile page.

```
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
```

### basketball-reference.com Team Page Scraper

The code in `bbref_team_scraper.py` can be used to scrape information from the NBA team pages (and easily adapted to CBB pages as well).
The urls for these pages take the form "www<i></i>.basketball-reference.com/teams/\[*TEAM-ABBREVIATION*\]/\[*SEASON*\].html".
For example, the team page for the 2016-17 Charlotte Hornets is at the following url: http://www.basketball-reference.com/teams/CHO/2017.html.
One word of warning, team abbreviations change from year to year (CHA vs CHO for Charlotte or NOH, NOK, or NOP for New Orleans).
In addition, teams enter and leave the league, so some error checking should be employed when navigating through multiple seasons or teams.
