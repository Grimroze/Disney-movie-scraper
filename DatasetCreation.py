#%%
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import time
import json
import os
import urllib
#%%
BASE_URL = "https://en.wikipedia.org"


def clean_tags(soup):
    for tag in soup.find_all(["sup", "span"]):
        tag.decompose()


def parse_movie_infobox(soup):
    info_box = soup.find("table", class_="infobox")
    if not info_box:
        return None
    info = {}
    rows = info_box.find_all("tr")
    clean_tags(soup)
    for i, row in enumerate(rows):
        if i == 0:
            th = row.find("th")
            if th:
                info['Title'] = th.get_text(" ", strip=True)
        elif i == 1:                                                # image
            continue
        else:
            header = row.find("th")
            data = row.find("td")
            if not (header and data):
                continue
            key = header.get_text(" ", strip=True)
            if data.find("li"):
                value = [li.get_text(strip=True).replace("\xa0", " ") for li in data.find_all("li")]
            elif data.find("br"):
                value = [text for text in data.stripped_strings]
            else:
                value = data.get_text(" ", strip=True).replace("\xa0", " ")
            info[key] = value
    return info



def scrape_movies(list_url, limit=None):
    resp = requests.get(list_url)
    resp.raise_for_status()
    soup = bs(resp.content)

    movie_links = []
    tables = soup.find_all("table", class_="wikitable")

    for table in tables:
        for row in table.find_all("tr")[1:]:
            cells = row.find_all("td")
            if len(cells) >= 2:
                # Get link from the second <td> (index 1)
                a = cells[1].find("a")
                if a and a.get("href", "").startswith("/wiki/"):
                    full_link = BASE_URL + a["href"]
                    movie_links.append(full_link)
    print(len(movie_links))                                     # Total scrapped movies

    if limit:
        movie_links = movie_links[:limit]

    movies = []
    for link in movie_links:
        try:
            r = requests.get(link)
            r.raise_for_status()
            sp = bs(r.content, "html.parser")
            data = parse_movie_infobox(sp)
            if data and 'Title' in data and data['Title'].strip() != '':
                data['url'] = link
                movies.append(data)
            time.sleep(0.0000001)                # respectful scraping
        except Exception as e:
            print(f"Skipping {link}: {e}")
    return movies

# Run the scraper
url = "https://en.wikipedia.org/wiki/List_of_Walt_Disney_Pictures_films"
movies = scrape_movies(url, limit=2)
for m in movies:
    print(m.get('Title', 'N/A'), "-", len(m.keys()) - 2, "fields")

print("Total scraped:", len(movies))
print(movies[1].get("Running time"))
#%%
def save_data(title,data):
    with open(title, 'w', encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii= False, indent=2)

def load_data(title):
    with open(title, 'r', encoding='utf-8') as f:
        return json.load(f)

save_data("Disney_data.json", movies)

movies = load_data("Disney_data.json")
#%% md
# Saving/Reloading data
#%% md
# Cleaning the data
#%%
# clean up references (remove [1],[2] etc)
# split up the long strings"
import re

def min_to_int(running_time):
    if isinstance(running_time, list):
        running_time = running_time[0]  # use first if it's a list

    if not isinstance(running_time, str):
        return None

    # Match the first number it sees
    match = re.search(r"\d+", running_time)
    if match:
        return int(match.group())

    return None  # If no digits found

#%%
# import copy
# movies_copy = copy.deepcopy(movies)

#%%
import re

def money_to_dollars(money_str):
    if isinstance(money_str, list):
        money_str = money_str[0]  # take first if list

    if not isinstance(money_str, str):
        return None

    money_str = money_str.replace(",", "").strip()

    match = re.search(r"(\d+(\.\d+)?)(?:\s*[–-]\s*(\d+(\.\d+)?))?\s*(million|billion)", money_str.lower())

    if not match:
        return None

    num = float(match.group(1))
    unit = match.group(5)

    if unit == "million":
        num *= 1_000_000
    elif unit == "billion":
        num *= 1_000_000_000

    return int(num)

#%%
from datetime import datetime

def extract_dates(date_list):
    if not isinstance(date_list, list):
        date_list = [date_list]

    cleaned_dates = []

    for date_str in date_list:
        # Remove things in parentheses like "(limited)"
        cleaned = re.sub(r"\(.*?\)", "", date_str).strip()
        try:
            dt = datetime.strptime(cleaned, "%B %d, %Y")
            cleaned_dates.append(dt)
        except Exception:
            continue  # skip if the format is weird

    return cleaned_dates
#%%
for mov in movies_copy:
    mov['Running time (int)'] = min_to_int(mov.get("Running time", ""))
    mov['Budget (USD)'] = money_to_dollars(mov.get("Budget", ""))
    mov['Box office (USD)'] = money_to_dollars(mov.get("Box office", ""))
    parsed = extract_dates(mov.get("Release dates", []))
    mov['First release date'] = parsed[0] if parsed else None
    mov.pop('Release dates (parsed)', None)
#%%
print([m.get('Running time (int)') for m in movies_copy])
#%%
movies_copy[90]
#%%
len(movies_copy)
#%%
import pickle

def save_data_pkl(name,data):
    with open(name, 'wb') as f:
        pickle.dump(data,f)

#%%
def load_data(name):
    with open(name,'rb') as f:
        return pickle.load(f)
#%%
save_data_pkl("Disney_data.pkl",movies_copy)
#%%
movies_cleaned = load_data("Disney_data.pkl")
#%%
len(movies_cleaned)
#%%
from dotenv import load_dotenv
import os

load_dotenv()
#%%
apikey = os.getenv("OMDB_API_KEY")
def get_omdb_info(title):
    base_url = "https://www.omdbapi.com/?"
    apikey = os.getenv("OMDB_API_KEY")
    if not apikey:
        raise ValueError("OMDB_API_KEY not found in environment.")
    params = {"apikey": apikey, "t": title}
    params_encoded = urllib.parse.urlencode(params)
    full_url = base_url + params_encoded
    return requests.get(full_url).json()

def get_rotten_tomatoes(omdb_info):
    if not omdb_info:
        return None
    ratings = omdb_info.get("Ratings", [])
    for r in ratings:
        if r.get("Source") == "Rotten Tomatoes":
            return r.get("Value")
    return None
#%%
info = get_omdb_info("the dark knight")
info
# get_rotten_tomatoes(info)
#%%
for m in movies_cleaned:
    title = m['Title']
    omdb_info = get_omdb_info(title)
    m['Imdb'] = omdb_info.get('imdbRating', None)
    m['Rotten Tomatoes'] = get_rotten_tomatoes(omdb_info)
    m['Metascore'] = omdb_info.get('Metascore',None)
    m['Genre'] = omdb_info.get('Genre', None)
    m['Imdb Votes'] = omdb_info.get('imdbVotes', None)
    m['Language'] = omdb_info.get('Language', None)
    m['Plot'] = omdb_info.get('Plot', None)
    m['Rated'] = omdb_info.get('Rated', None)
    m['Awards'] = omdb_info.get('Awards', None)

#%%
movies_cleaned[218]
#%%
save_data_pkl("Disney_data_final.pkl",movies_cleaned)
#%%
moviesCopy = [movies.copy() for movies in movies_cleaned]
#%%
moviesCopy[56]
#%%
for m in moviesCopy:
    curr_date = m['First release date']
    if curr_date:
        m['First release date'] = curr_date.strftime("%B %d, %Y")
    else:
        m['First release date'] = None
#%%
moviesCopy[6]
#%%
save_data("movies_data.json",moviesCopy)
#%%
df = pd.DataFrame(movies_cleaned)
#%%
df.head()
#%%
df.info
#%%
