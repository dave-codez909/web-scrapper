import requests
from bs4 import BeautifulSoup
import threading

url = 'https://animepahe.ru/'
threads = []

def get_anime_list(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for request errors
        soup = BeautifulSoup(response.text, 'html.parser')

        # Inspect the page and change the class/tag as needed
        articles = soup.find_all('div', class_='content-wrapper')
        
        if not articles:
            print(f"No articles found on {url}")
            return

        for article in articles:
            title = article.find('h2').text if article.find('h2') else 'No Title'
            link = article.find('a')['href'] if article.find('a') else '#'
            print(f"Title: {title}")
            print(f"Link: {url + link}")
            print('---')
    except requests.RequestException as e:
        print(f"Request error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Thread function to start scraping in a new thread
def start_scraping(url):
    thread = threading.Thread(target=get_anime_list, args=(url,))
    threads.append(thread)
    thread.start()

# Start the scraping process
start_scraping(url)

# Wait for all threads to complete
for thread in threads:
    thread.join()

print('Scraping completed.')