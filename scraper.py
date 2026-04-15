import feedparser
import csv
import os
import re
import requests

RSS_URL = "https://www.blu-ray.com/rss/newsfeed.xml"
CSV_FILE = "commentary_releases.csv"
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")

def clean_html(raw_html):
    """Removes HTML tags from the summary paragraph so it reads cleanly."""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()

def get_direct_link(title):
    """Uses SerpApi to bypass bot blockers and grab the exact product URL."""
    if not SERPAPI_KEY:
        return "API Key Missing"
    
    clean_title = re.sub(r'(4K|Blu-ray|UHD|Standard Edition|Limited Edition|\(\))', '', title, flags=re.IGNORECASE).strip()
    query = f"{clean_title} blu-ray site:criterion.com OR site:kinolorber.com OR site:arrowvideo.com OR site:amazon.com"
    url = f"https://serpapi.com/search.json?q={query}&api_key={SERPAPI_KEY}"
    
    try:
        response = requests.get(url).json()
        if "organic_results" in response and len(response["organic_results"]) > 0:
            return response["organic_results"][0]["link"]
    except Exception as e:
        print(f"Search failed for {title}: {e}")
        
    return "Manual search required"

def main():
    print("Fetching Blu-ray news feed...")
    feed = feedparser.parse(RSS_URL)
    existing_titles = set()
    
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None) 
            for row in reader:
                if len(row) > 0:
                    existing_titles.add(row[0]) # Tracks by Title to avoid duplicates

    new_entries = []
    
    for entry in feed.entries:
        title = entry.title
        desc = entry.description
        pub_date = entry.published

        content_str = (title + " " + desc).lower()
        
        # We are back to strictly searching for "commentary"
        if "commentary" in content_str and title not in existing_titles:
            print(f"New commentary found: {title}. Hunting for direct link...")
            direct_link = get_direct_link(title)
            clean_desc = clean_html(desc)
            new_entries.append([title, pub_date, clean_desc, direct_link])

    if new_entries:
        mode = 'a' if os.path.exists(CSV_FILE) else 'w'
        with open(CSV_FILE, mode, newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if mode == 'w':
                writer.writerow(["Title", "Date Announced", "Release Summary", "Direct Purchase Link"])
            writer.writerows(new_entries)
        print(f"Success! Added {len(new_entries)} new releases to the database.")
    else:
        print("No new commentary tracks announced today.")

if __name__ == "__main__":
    main()
