import requests 
from bs4 import BeautifulSoup
import threading

url = ""
threads = []

def get_anime_list():
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    for link in soup.find_all('a', href=True):
        thread = threading.Thread(target=get_anime_list, args=(link['href'],))
        threads.append(thread)
        thread.start()

def get_anime_details(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    anime_name = soup.find('h1', class_='title-name').text.strip()
    episodes = soup.find('span', itemprop='numberOfEpisodes').text.strip()
    genres = [genre.text.strip() for genre in soup.find_all('span', itemprop='genre')]
    
    print(f"Anime Name: {anime_name}")
    print(f"Episodes: {episodes}")
    print(f"Genres: {', '.join(genres)}")
    print()