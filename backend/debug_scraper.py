"""Debug scraper API calls"""
import requests
from urllib.parse import quote

# --- Test Steam ---
print("=== Steam API (cc=CN) ===")
url = f'https://store.steampowered.com/api/storesearch?term={quote("Elden Ring")}&l=schinese&cc=CN'
r = requests.get(url, timeout=15)
data = r.json()
print(f"Total: {data.get('total', 0)}, Items: {len(data.get('items', []))}")
items = data.get('items', [])
if items:
    first = items[0]
    print(f"First: id={first.get('id')}, name={first.get('name')}")
    # Get detail
    detail_url = f'https://store.steampowered.com/api/appdetails?appids={first["id"]}&l=schinese'
    dr = requests.get(detail_url, timeout=15)
    dd = dr.json()
    if dd.get(str(first['id']), {}).get('success'):
        gd = dd[str(first['id'])]['data']
        print(f"  Type: {gd.get('type')}")
        print(f"  Name: {gd.get('name')}")
        print(f"  Genres: {[g.get('description') for g in gd.get('genres', [])]}")
        print(f"  Header: {gd.get('header_image', '')[:80]}")
        print(f"  Intro: {gd.get('short_description', '')[:100]}")
        print(f"  Release: {gd.get('release_date', {})}")
    else:
        print(f"  Detail failed: {dd}")

# --- Test Douban ---
print("\n=== Douban ===")
from bs4 import BeautifulSoup
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
r = requests.get(f'https://www.douban.com/search?cat=1005&q={quote("艾尔登法环")}', headers=headers, timeout=15)
soup = BeautifulSoup(r.text, 'lxml')
result = soup.select_one('.result')
if result:
    title_e = result.select_one('.title a')
    detail_url = title_e.get('href') if title_e else None
    print(f"Title: {title_e.text.strip() if title_e else 'N/A'}")
    print(f"Detail URL: {detail_url}")

    rating_e = result.select_one('.rating_nums')
    print(f"Rating: {rating_e.text.strip() if rating_e else 'N/A'}")

    if detail_url:
        dr = requests.get(detail_url, headers=headers, timeout=15)
        ds = BeautifulSoup(dr.text, 'lxml')
        tags = ds.select('span[property="v:genre"]')
        print(f"Tags from detail: {[t.text.strip() for t in tags]}")
        intro = ds.select_one('#link-report .intro') or ds.select_one('[property="v:summary"]')
        if intro:
            print(f"Intro: {intro.get_text(strip=True)[:150]}")

