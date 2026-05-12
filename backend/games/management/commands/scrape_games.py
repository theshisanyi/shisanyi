from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from games.models import Game, Category
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import os
import re
from io import BytesIO
from datetime import datetime


class Command(BaseCommand):
    help = '从 Steam 和豆瓣爬取游戏信息并入库'

    def add_arguments(self, parser):
        parser.add_argument('game_names', nargs='+', type=str, help='要爬取的游戏名称（多个）')
        parser.add_argument('--dry-run', action='store_true', help='只显示爬取结果，不入库')
        parser.add_argument('--update', action='store_true', help='更新已存在的游戏数据')

    def handle(self, *args, **options):
        for name in options['game_names']:
            self.stdout.write(f'\n===== 正在爬取: {name} =====')
            try:
                steam_data = self.scrape_steam(name)
                self.stdout.write(f'  Steam: {"获取到数据" if steam_data else "未找到"}')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  Steam 爬取失败: {e}'))
                steam_data = {}

            try:
                douban_data = self.scrape_douban(name)
                self.stdout.write(f'  豆瓣: {"获取到数据" if douban_data else "未找到"}')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  豆瓣爬取失败: {e}'))
                douban_data = {}

            merged = self.merge_data(name, steam_data, douban_data)

            self.stdout.write(f'  标题: {merged.get("title", "N/A")}')
            self.stdout.write(f'  标签: {", ".join(merged.get("tags", []))}')

            if options['dry_run']:
                self.stdout.write(self.style.SUCCESS('  [dry-run] 未入库'))
                continue

            self.save_game(merged, update=options['update'])

    def scrape_steam(self, name):
        """通过 Steam Storefront API 搜索游戏"""
        # Search (need cc=CN for Chinese region results)
        search_url = f'https://store.steampowered.com/api/storesearch?term={quote(name)}&l=schinese&cc=CN'
        resp = requests.get(search_url, timeout=30)
        resp.raise_for_status()
        items = resp.json().get('items', [])
        if not items:
            return {}

        appid = items[0]['id']

        # Get details
        detail_url = f'https://store.steampowered.com/api/appdetails?appids={appid}&l=schinese'
        resp = requests.get(detail_url, timeout=15)
        resp.raise_for_status()
        detail = resp.json()
        data = detail.get(str(appid), {}).get('data', {})

        if not data or data.get('type') != 'game':
            return {}

        # Parse release date
        release_info = data.get('release_date', {})
        release_date = release_info.get('date', '')
        if release_date:
            try:
                for fmt in ('%d %b, %Y', '%Y年%m月%d日', '%b %d, %Y', '%Y-%m-%d'):
                    try:
                        release_date = datetime.strptime(release_date, fmt).strftime('%Y-%m-%d')
                        break
                    except ValueError:
                        continue
            except Exception:
                pass

        return {
            'title': data.get('name', name),
            'official_intro': data.get('short_description', ''),
            'cover_image_url': data.get('header_image', ''),
            'release_date': release_date if release_date and release_date != '' else None,
            'purchase_link': f'https://store.steampowered.com/app/{appid}',
            'tags': [tag.get('description', '') for tag in data.get('genres', [])],
        }

    def scrape_douban(self, name):
        """从豆瓣搜索游戏，获取标题和评分"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        search_url = f'https://www.douban.com/search?cat=1005&q={quote(name)}'
        resp = requests.get(search_url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'lxml')

        result = soup.select_one('.result')
        if not result:
            return {}

        # Get title
        title_elem = result.select_one('.title a')
        title = title_elem.text.strip() if title_elem else name

        # Get rating
        rating = 0
        rating_elem = soup.select_one('.rating_nums')
        if not rating_elem:
            rating_elem = result.select_one('.rating_nums')
        if rating_elem:
            try:
                rating = float(rating_elem.text.strip())
            except ValueError:
                rating = 0

        # Get tags from result content (Douban search results have limited structured tag data)
        tags = []
        content_elem = result.select_one('.content p') or result.select_one('.content')
        if content_elem:
            text = content_elem.get_text(' ', strip=True)
            # Split into potential tag fragments
            parts = [p.strip() for p in re.split(r'[，,、/\s]+', text) if len(p.strip()) >= 2]
            # Exclude non-tag patterns
            exclude_patterns = ['人关注', '人评价', '人玩过', '人在玩', '人想玩', '人在做',
                               '上海', '北京', '深圳', '广州', '杭州', '成都', '豆瓣']
            tags = [p for p in parts
                    if not any(ep in p for ep in exclude_patterns)
                    and not re.match(r'^\d+$', p)
                    and p != title
                    and p != name][:6]

        return {
            'douban_title': title,
            'douban_rating': rating,
            'tags': tags,
        }

    def merge_data(self, search_name, steam, douban):
        """合并 Steam 和豆瓣数据，豆瓣中文信息优先"""
        title = douban.get('douban_title') or steam.get('title', search_name)
        rating = douban.get('douban_rating') or 0
        tags = list(dict.fromkeys(douban.get('tags', []) + steam.get('tags', [])))
        # 简介：豆瓣优先，Steam 补充
        intro = douban.get('douban_intro', '') or steam.get('official_intro', '')

        return {
            'title': title,
            'rating': float(rating) if rating else 0,
            'official_intro': intro,
            'cover_image_url': steam.get('cover_image_url', ''),
            'purchase_link': steam.get('purchase_link', ''),
            'release_date': steam.get('release_date'),
            'tags': tags,
        }

    def save_game(self, data, update=False):
        """保存或更新游戏数据"""
        title = data['title']
        game = Game.objects.filter(title=title).first()

        if game and not update:
            self.stdout.write(self.style.WARNING(f'  游戏 "{title}" 已存在，跳过（使用 --update 更新）'))
            return

        if game:
            for key in ['official_intro', 'purchase_link', 'release_date']:
                if data.get(key):
                    setattr(game, key, data[key])
            game.rating = data.get('rating', game.rating)
            game.save()
            self.stdout.write(self.style.SUCCESS(f'  已更新: {title}'))
        else:
            game = Game.objects.create(
                title=title,
                rating=data.get('rating', 0),
                official_intro=data.get('official_intro', ''),
                purchase_link=data.get('purchase_link', ''),
                release_date=data.get('release_date'),
            )
            self.stdout.write(self.style.SUCCESS(f'  已创建: {title}'))

        # Tags
        categories = []
        for tag_name in data.get('tags', []):
            cat, _ = Category.objects.get_or_create(
                name=tag_name,
                defaults={'slug': re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]+', '-', tag_name).strip('-').lower() or tag_name}
            )
            categories.append(cat)
        game.categories.set(categories)

        # Download cover image
        cover_url = data.get('cover_image_url')
        if cover_url and not game.cover_image:
            try:
                resp = requests.get(cover_url, timeout=20)
                if resp.status_code == 200:
                    ext = cover_url.split('.')[-1].split('?')[0] or 'jpg'
                    safe_title = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]+', '_', title)
                    filename = f"{game.id}_{safe_title}.{ext}"
                    game.cover_image.save(filename, ContentFile(resp.content), save=True)
                    self.stdout.write(f'  封面已下载')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  封面下载失败: {e}'))

        self.stdout.write(self.style.SUCCESS(f'  标签: {", ".join(data.get("tags", []))}'))
