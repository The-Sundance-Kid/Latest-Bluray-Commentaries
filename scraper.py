import feedparser
import csv
import os
import re
from duckduckgo_search import DDGS

RSS_URL = "https://www.blu-ray.com/rss/newsfeed.xml"
CSV_FILE = "commentary_releases.csv"

def get_direct_link(title):
    clean_title = re.sub(r'(4K|Blu-ray|UHD|Standard Edition|Limited Edition|\(\))', '', title, flags=re.IGNORECASE).strip()
    query = f"{clean_title} blu-ray site:criterion.com OR site:kinolorber.com OR site:arrowvideo.com OR site:amazon.com"
    
    try:
        results = DDGS().text(query, max_results=1)
        for r in results:
            return r['href'] 
    except Exception as e:
        print(f"Search failed for {title}: {e}")
        return "Manual search required"
    return "Link not found"

def main():
    print("Fetching Blu-ray news feed...")
    feed = feedparser.parse(RSS_URL)
    existing_links = set()
    
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None) 
            for row in reader:
                if len(row) > 2:
                    existing_links.add(row[2])

    new_entries = []
    
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        desc = entry.description
        pub_date = entry.published

        content_str = (title + " " + desc).lower()
        
        # NOTE: Temporarily searching for '4k' to force a successful test!
        if "4k" in content_str and link not in existing_links:
            print(f"New release found: {title}. Hunting for direct link...")
            direct_link = get_direct_link(title)
            new_entries.append([title, pub_date, link, direct_link])

    if new_entries:
        mode = 'a' if os.path.exists(CSV_FILE) else 'w'
        with open(CSV_FILE, mode, newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if mode == 'w':
                writer.writerow(["Title", "Date Announced", "News Link", "Direct Purchase Link"])
            writer.writerows(new_entries)
        print(f"Success! Added {len(new_entries)} new releases to the database.")
    else:
        print("No new tracks announced today.")

if __name__ == "__main__":
    main()
