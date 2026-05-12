"""Test using Bing search to find game pages on target sites"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

name = '艾尔登法环'

# Try Bing search with site: filter
for site_name, site_domain in [('游侠', 'ali213.net'), ('3DM', '3dmgame.com'), ('逗游', 'doyo.cn')]:
    print(f"\n=== {site_name} (Bing search: site:{site_domain} {name}) ===")
    query = f'site:{site_domain} {name}'
    url = f'https://www.bing.com/search?q={quote(query)}'
    try:
        r = requests.get(url, headers=headers, timeout=15)
        print(f"  Status: {r.status_code}, len: {len(r.text)}")
        soup = BeautifulSoup(r.text, 'lxml')

        # Bing search result links
        results = soup.select('#b_results .b_algo h2 a, #b_results li h2 a, .b_title a')
        if not results:
            results = soup.select('h2 a[href]')
        
        print(f"  Found {len(results)} search results")
        for res in results[:5]:
            href = res.get('href', '')
            text = res.get_text(strip=True)
            if site_domain in href:
                print(f"    MATCH: {text[:50]} -> {href[:80]}")
        
        # Sometimes results are in cite tags
        cites = soup.select('.b_caption cite, .b_attribution cite')
        for cite in cites[:5]:
            print(f"    cite: {cite.get_text(strip=True)[:80]}")

    except Exception as e:
        print(f"  ERR: {e}")
