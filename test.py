import requests
import sqlite3
import threading
import time

# GraphQL query for fetching anime list with IDs and images
query = '''
query ($page: Int, $perPage: Int) {
  Page(page: $page, perPage: $perPage) {
    media(type: ANIME, sort: POPULARITY_DESC) {
      id
      title {
        romaji
        english
      }
      episodes
      genres
      description
      coverImage {
        large
      }
    }
  }
}
'''

url = "https://graphql.anilist.co"
database = 'anime.db'
threads = []
max_retries = 3  # Number of retries for each request
retry_delay = 5  # Delay between retries in seconds

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS anime (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title_romaji TEXT,
            title_english TEXT,
            episodes INTEGER,
            genres TEXT,
            description TEXT,
            url TEXT,
            cover_image TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Function to save anime data to the database
def save_to_db(anime_list):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    for anime in anime_list:
        anime_url = f"https://anilist.co/anime/{anime['id']}"  # Construct AniList URL using the anime ID
        cover_image_url = anime.get('coverImage', {}).get('large', '')

        cursor.execute('''
            INSERT INTO anime (title_romaji, title_english, episodes, genres, description, url, cover_image)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            anime['title']['romaji'],
            anime['title']['english'],
            anime['episodes'],
            ', '.join(anime['genres']),
            anime['description'][:500],  # Limit description to 500 characters
            anime_url,
            cover_image_url
        ))
    
    conn.commit()
    conn.close()

# Function to scrape anime data from AniList with retry logic
def scrape_anime(page):
    variables = {
        'page': page,
        'perPage': 50  # Number of anime to fetch per page
    }

    for attempt in range(max_retries):
        response = requests.post(url, json={'query': query, 'variables': variables})
        
        if response.status_code == 200:
            data = response.json()
            anime_list = data['data']['Page']['media']

            if anime_list:
                save_to_db(anime_list)  # Save data to the database
                print(f"Page {page} scraped successfully. Total: {len(anime_list)} anime.")
            else:
                print(f"No anime data on page {page}.")
            break
        elif response.status_code == 429:
            print(f"Rate limit exceeded for page {page}. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            print(f"Error fetching data from page {page}: {response.status_code}")
            break

# Main function to scrape all pages with threading
def scrape_all_anime():
    # Reduce the number of concurrent threads to avoid hitting rate limits
    for page in range(1, 101):  
        thread = threading.Thread(target=scrape_anime, args=(page,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    init_db()  # Initialize the database
    scrape_all_anime()
