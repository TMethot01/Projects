from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import json
from ics import Calendar, Event
from datetime import datetime
import pytz

def fetch_movie_release(url):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }   
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    movies = []
    
    date_sections = soup.find_all('article', attrs={"data-testid": "calendar-section"})
    for section in date_sections:

        date = section.find('h3', class_="ipc-title__text").text

        movie_entries = section.find_all('li', attrs={"data-testid": "coming-soon-entry"})
        for movie_entry in movie_entries:
            
            unformated_title = movie_entry.find('a', {'class': 'ipc-metadata-list-summary-item__t'}).text            
            title, _, _ = unformated_title.rpartition(' (')

            movies.append((title, date))
    return movies


def save_movies(movies):
    with open('movies_coming_soon.json', 'w') as f:
        json.dump(movies, f)


def create_calendar(movies):
    cal = Calendar()
    tz = pytz.timezone("America/New_York")
    for name, date in movies:
        event = Event()
        event.name = name
        event.begin = tz.localize(datetime.strptime(date, '%b %d, %Y'))  # Adjust the format according to your data
        cal.events.add(event)
    with open('movies.ics', 'w') as my_file:
        my_file.writelines(str(cal))


coming_soon = fetch_movie_release("https://www.imdb.com/calendar/?ref_=rlm&region=CA&type=MOVIE")
save_movies(coming_soon)
create_calendar(coming_soon)
print(coming_soon)