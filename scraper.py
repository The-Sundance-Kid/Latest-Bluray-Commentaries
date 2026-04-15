import feedparser
import csv
import os
import urllib.parse
import re

RSS_URL = "https://www.blu-ray.com/rss/newsfeed.xml"
CSV_FILE = "commentary_releases.csv"

def generate_order_link(title, description):
    """Routes the title to the correct boutique label's storefront search."""
    clean_title = re.sub(r'(4K|Blu-ray|UHD|Standard Edition|Limited Edition|\(\))', '', title, flags=re.IGNORECASE).strip()
    encoded_title = urllib.parse.quote_plus(clean_title)
    content_str = (title + " " + description).lower()

    if "criterion" in content_str:
        return f"https://www.criterion.com/shop/browse?q={encoded_title}"
    elif "kino lorber" in content_str or "kino studio classics" in content_str:
        return f"https://kinolorber.com/search?q={encoded_title}"
    elif "arrow video" in content_str:
        return f"https://www.arrowvideo.com/elysium.search?search={encoded_title}"
    elif "shout! factory" in content_str or "scream factory" in content_str:
        return f"https://shoutfactory.com/search?q={encoded_title}"
    elif "vinegar syndrome" in content_str or "cinématographe" in content_str:
        return f"https://vinegarsyndrome.com/search?q={encoded_title}"
    else:
        return f"https://www.amazon.com/s?k={encoded_title}+blu-ray"

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
        
        # NOTE: Still using the "4k" stress test so it works immediately!
        if "4k" in content_str and link not in existing_links:
            print(f"New release found: {title}. Generating direct search link...")
            order_link = generate_order_link(title, desc)
            new_entries.append([title, pub_date, link, order_link])

    if new_entries:
        mode = 'a' if os.path.exists(CSV_FILE) else 'w'
        with open(CSV_FILE, mode, newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if mode == 'w':
                writer.writerow(["Title", "Date Announced", "News Link", "Order Link"])
            writer.writerows(new_entries)
        print(f"Success! Added {len(new_entries)} new releases to the database.")
    else:
        print("No new tracks announced today.")

if __name__ == "__main__":
    main()
