import pymongo
from pymongo.errors import ServerSelectionTimeoutError
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def get_week_dates(week_offset=0):
    """Returns the start (Friday) and end (Thursday) dates of the week for a given offset."""
    today = datetime.today().date()  # Get today's date without time
    
    # Calculate the start of the current week (Friday)
    start_of_current_week = today - timedelta(days=(today.weekday() + 3) % 7)
    
    # Calculate the start of the target week
    start_of_target_week = start_of_current_week + timedelta(days=7 * week_offset)
    
    # Calculate the end of the target week (Thursday)
    end_of_target_week = start_of_target_week + timedelta(days=6)
    
    return start_of_target_week, end_of_target_week

def extract_movie_data(url, cookies, headers, start_date, end_date):
    """
    Extracts movie data from the specified URL using provided cookies and headers.
    Only processes articles where the release date falls between start_date and end_date.
    """

    print (start_date, "start date")
    try:
        response = requests.get(url, cookies=cookies, headers=headers)
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        
        soup = BeautifulSoup(response.content, 'html.parser')
        article_elements = soup.find_all('article', {'data-testid': 'calendar-section'})
        movies = []

        for article in article_elements:
            release_date_text = article.find('h3', class_='ipc-title__text').text.strip() if article.find('h3', class_='ipc-title__text') else None
            
            if release_date_text:
                # Convert release date to datetime object
                try:
                    release_date = datetime.strptime(release_date_text, '%b %d, %Y').date()
                except ValueError:
                    continue  # Skip if the date format is not as expected
                
                # Filter by date range
                if start_date <= release_date <= end_date:
                    movie_list = article.find_all('li', class_='ipc-metadata-list-summary-item')
                    
                    for movie_item in movie_list:
                        movie_title = movie_item.find('a', class_='ipc-metadata-list-summary-item__t').text.strip() if movie_item.find('a', class_='ipc-metadata-list-summary-item__t') else None
                        movie_link = movie_item.find('a', class_='ipc-metadata-list-summary-item__t')['href'] if movie_item.find('a', class_='ipc-metadata-list-summary-item__t') else None

                        if movie_title and release_date_text and movie_link:
                            # Extract the movie ID from the link
                            movie_id = movie_link.split('/')[2]

                            movies.append({
                                '_id': movie_id,
                                'title': movie_title,
                                'release_date': release_date_text,
                                'movie_link': movie_link,
                            })
                            
        print(movies, "movies")
        return movies

    except Exception as e:
        print(f"Error extracting data: {e}")
        return []

def get_imdb_movie_details(url, cookies, headers):
    """Fetches and parses IMDb movie details for a given URL."""
    try:
        response = requests.get(url, cookies=cookies, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        movie_details = {}

        movie_title_element = soup.find('h1', class_='sc-d8941411-0 dxeMrU')
        if movie_title_element:
            movie_details['title'] = movie_title_element.find('span', class_='hero__primary-text').text.strip()
        else:
            movie_details['title'] = ''

        release_info_list = soup.find('ul', class_='ipc-inline-list ipc-inline-list--show-dividers sc-d8941411-2 kRgWEf baseAlt')
        if release_info_list:
            release_info = release_info_list.find_all('li')
            movie_details['release_year'] = release_info[0].text.strip() if len(release_info) > 0 else ''
            movie_details['certification'] = release_info[1].text.strip() if len(release_info) > 1 else ''
            movie_details['duration'] = release_info[-1].text.strip() if len(release_info) > 2 else ''
        else:
            movie_details['release_year'] = ''
            movie_details['certification'] = ''
            movie_details['duration'] = ''

        genre_info_list = soup.find('div', class_='ipc-chip-list__scroller')
        if genre_info_list:
            movie_details['genres'] = [genre.text.strip() for genre in genre_info_list.find_all('a')]
        else:
            movie_details['genres'] = []

        plot_element = soup.find('span', {'data-testid': 'plot-xl'})
        if plot_element:
            movie_details['plot'] = plot_element.text.strip()
        else:
            movie_details['plot'] = ''

        popularity_element = soup.find('div', {'data-testid': 'hero-rating-bar__popularity__score'})
        if popularity_element:
            movie_details['popularity'] = popularity_element.text.strip()
        else:
            movie_details['popularity'] = ''

        rating_element = soup.find('span', class_="sc-eb51e184-1 ljxVSS")
        if rating_element:
            movie_details['rating'] = rating_element.text.strip()
        else:
            movie_details['rating'] = ''

        rating_count_element = soup.find('div', class_="sc-eb51e184-3 kgbSIj")
        if rating_count_element:
            movie_details['rating_count'] = rating_count_element.text.strip()
        else:
            movie_details['rating_count'] = ''

        # Extract crew information directly
        crew_data = {}
        target_ul = soup.find('ul', class_='ipc-metadata-list ipc-metadata-list--dividers-all title-pc-list ipc-metadata-list--baseAlt')
        if target_ul:
            for li in target_ul.find_all('li', {'data-testid': 'title-pc-principal-credit'}):
                crew_type_element = li.find(True)
                if crew_type_element:
                    crew_type = crew_type_element.text.strip()
                    div_element = li.find('div')
                    if div_element:
                        crew_list_element = div_element.find('ul')
                        if crew_list_element:
                            crew_members = [crew_member.text.strip() for crew_member in crew_list_element.find_all('li')]
                            movie_details[crew_type] = crew_members
        else:
            movie_details['Director'] = []
            movie_details['Writers'] = []
            movie_details['Stars'] = []

        # Extract image URL (adjust selector as needed)
        anchor_tag = soup.find('a', class_='ipc-lockup-overlay ipc-focusable')
        if anchor_tag:
            parent_element = anchor_tag.parent
            image_tag = parent_element.find('img')
            if image_tag:
                movie_details['image_url'] = image_tag['src']
            else:
                movie_details['image_url'] = ''
        else:
            movie_details['image_url'] = ''

        return movie_details

    except requests.exceptions.RequestException as e:
        print(f"Error fetching movie details: {e}")
        return None

def save_to_mongodb(movies, mongodb_uri, collection_name, cookies, headers):
    """Saves or updates extracted movie data to a MongoDB database."""
    try:
        client = pymongo.MongoClient(mongodb_uri)
        db = client["imdbcalendar"]
        collection = db[collection_name]
        print(movies)

        for movie in movies:
            movie_id = movie['_id']
            movie_details = get_imdb_movie_details(f'https://www.imdb.com/title/{movie_id}/', cookies, headers)
            
            if movie_details:
                existing_movie = collection.find_one({'_id': movie_id})
                
                # Prepare a document with default empty values if not present
                update_fields = {
                    'title': '',
                    'release_year': '',
                    'certification': '',
                    'duration': '',
                    'genres': [],
                    'plot': '',
                    'popularity': '',
                    'rating': '',
                    'rating_count': '',
                    'Director': [],
                    'Writers': [],
                    'Stars': [],
                    'image_url': '',
                    'uploaded': False 
                }
                print(update_fields)
                
                # Update with new values if present
                update_fields.update(movie_details)
                
                if existing_movie:
                    for key, value in update_fields.items():
                        if existing_movie.get(key) != value:
                            update_fields[key] = value
                    update_fields['uploaded'] = True  # Ensure uploaded is set to True for updated details

                # Perform the update with only changed fields
                collection.update_one(
                    {'_id': movie_id},
                    {'$set': update_fields},
                    upsert=True
                )
                print(f"Updated movie with ID: {movie_id} with changes: {update_fields}")
            else:
                print(f"Error fetching details for movie with ID: {movie_id}")

    except ServerSelectionTimeoutError as e:
        print(f"Error connecting to MongoDB: {e}")
    finally:
        client.close()

def main():
    """Main function to run the script"""
    # Define your parameters here
    url = 'https://www.imdb.com/calendar/'

    cookies = {
        'session-id': '147-9820983-8069527',
        'session-id-time': '2082787201l',
        'ad-oo': '0',
        'csm-hit': 'tb:BKW4R0YR33DDACRBJYWR+s-BKW4R0YR33DDACRBJYWR|1723546810308&t:1723546810308&adb:adblk_no',
        'ci': 'e30',
    }

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        # 'cookie': 'session-id=147-9820983-8069527; session-id-time=2082787201l; ad-oo=0; csm-hit=tb:BKW4R0YR33DDACRBJYWR+s-BKW4R0YR33DDACRBJYWR|1723546810308&t:1723546810308&adb:adblk_no; ci=e30',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    }
    mongodb_uri = 'mongodb+srv://cinefav:cinefav@cluster0.nsbu5lq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'  # Update as needed
    start_date, end_date = get_week_dates(0)  # Get dates for the coming week
    # Format the start_date to a string suitable for a collection name
    formatted_start_date = start_date.strftime('%Y-%m-%d')  # For example, '2024-08-13'

# Create the collection name by concatenating the string 'movies' with the formatted date
    collection_name = 'movies_' + formatted_start_date
    movies = extract_movie_data(url, cookies, headers, start_date, end_date)
    save_to_mongodb(movies, mongodb_uri, collection_name, cookies, headers)


    start_date, end_date = get_week_dates(1)  # Get dates for the coming week
    # Format the start_date to a string suitable for a collection name
    formatted_start_date = start_date.strftime('%Y-%m-%d')  # For example, '2024-08-13'

# Create the collection name by concatenating the string 'movies' with the formatted date
    collection_name = 'movies_' + formatted_start_date
    movies = extract_movie_data(url, cookies, headers, start_date, end_date)
    save_to_mongodb(movies, mongodb_uri, collection_name, cookies, headers)

if __name__ == '__main__':
    main()
