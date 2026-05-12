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
    help = '从 Steam、豆瓣、游侠、逗游、3DM 爬取游戏信息并入库'

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

            try:
                youxia_data = self.scrape_youxia(name)
                self.stdout.write(f'  游侠: {"获取到数据" if youxia_data else "未找到"}')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  游侠爬取失败: {e}'))
                youxia_data = {}

            try:
                doyo_data = self.scrape_doyo(name)
                self.stdout.write(f'  逗游: {"获取到数据" if doyo_data else "未找到"}')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  逗游爬取失败: {e}'))
                doyo_data = {}

            try:
                threedm_data = self.scrape_3dm(name)
                self.stdout.write(f'  3DM: {"获取到数据" if threedm_data else "未找到"}')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  3DM爬取失败: {e}'))
                threedm_data = {}

            merged = self.merge_data(name, steam_data, douban_data, youxia_data, doyo_data, threedm_data)

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
        raw_date = release_info.get('date', '')
        release_date = None
        if raw_date:
            try:
                for fmt in ('%Y 年 %m 月 %d 日', '%Y年%m月%d日', '%d %b, %Y', '%b %d, %Y', '%Y-%m-%d'):
                    try:
                        release_date = datetime.strptime(raw_date, fmt).strftime('%Y-%m-%d')
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
            # 豆瓣搜索结果通常不含游戏类型标签，只含评价信息
            # 只有长度<=4且只含中文的可能是标签
            parts = [p.strip() for p in re.split(r'[，,、/\s]+', text) if 2 <= len(p.strip()) <= 4]
            exclude_patterns = ['人关注', '人评价', '人玩过', '人在玩', '人想玩', '人在做',
                               '上海', '北京', '深圳', '广州', '杭州', '成都', '豆瓣', '评分']
            tags = [p for p in parts
                    if not any(ep in p for ep in exclude_patterns)
                    and not re.match(r'^\d+', p)
                    and p != title
                    and p != name
                    and re.match(r'^[\u4e00-\u9fff]+$', p)][:4]  # 只取纯中文短词

        return {
            'douban_title': title,
            'douban_rating': rating,
            'tags': tags,
        }

    def scrape_youxia(self, name):
        """从游侠网 (ali213.net) 搜索游戏信息（通过Bing）"""
        return self._search_site(name, 'ali213.net', '游侠')

    def scrape_doyo(self, name):
        """从逗游 (doyo.cn) 搜索游戏信息（通过Bing）"""
        return self._search_site(name, 'doyo.cn', '逗游')

    def scrape_3dm(self, name):
        """从3DM (3dmgame.com) 搜索游戏信息（通过Bing）"""
        return self._search_site(name, '3dmgame.com', '3DM')

    def _search_site(self, name, domain, label):
        """通过 Bing 搜索指定站点内的游戏页面"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        try:
            # 1. Bing 搜索
            query = f'site:{domain} {name}'
            search_url = f'https://www.bing.com/search?q={quote(query)}'
            r = requests.get(search_url, headers=headers, timeout=15)
            soup = BeautifulSoup(r.text, 'lxml')

            # 2. 找站点链接
            game_url = None
            game_title = name
            for sel in ['.b_algo h2 a', '#b_results h2 a', '.b_title a', 'h2 a[href]']:
                for a in soup.select(sel):
                    href = a.get('href', '')
                    text = a.get_text(strip=True)
                    if domain in href and 'search' not in href.lower():
                        game_url = href
                        game_title = text.split('_')[0].strip() if '_' in text else text
                        break
                if game_url:
                    break

            if not game_url:
                return {}

            # 3. 访问游戏详情页
            r2 = requests.get(game_url, headers=headers, timeout=15)
            soup2 = BeautifulSoup(r2.content, 'lxml')

            # ---- 封面图 (优先 OG 标签, 其次页面第一张大图) ----
            cover_url = ''
            og_img = soup2.select_one('meta[property="og:image"]')
            if og_img:
                cover_url = og_img.get('content', '')

            if not cover_url:
                # 找页面主图（多种选择器）
                for sel in ['.game-cover img', '.detail-cover img', '.game-img img',
                            '.pic-show img', '.pic img', '[class*="cover"] img',
                            '.banner img', 'img.banner', '[class*="banner"] img']:
                    img = soup2.select_one(sel)
                    if img:
                        src = img.get('src') or img.get('data-src') or ''
                        if src and len(src) > 15:
                            cover_url = src
                            break

            if not cover_url:
                # 取文件名含 banner/cover/thumb 的图片（排除 logo/head）
                for img in soup2.select('img[src]')[:30]:
                    src = img.get('src', '')
                    if src and ('banner' in src or 'cover' in src or 'thumb' in src):
                        if 'logo' not in src.lower() and 'head' not in src.lower():
                            cover_url = src
                            break

            if not cover_url:
                # 取第一张 .jpg/.png 但排除 logo/icon/head
                for img in soup2.select('img[src]')[:30]:
                    src = img.get('src', '')
                    ext = src.rsplit('.', 1)[-1].lower() if '.' in src else ''
                    low = src.lower()
                    if (src and ext in ('jpg', 'jpeg', 'png', 'webp')
                            and 'icon' not in low and 'logo' not in low and 'head' not in low
                            and 'qr' not in low):
                        cover_url = src
                        break

            if cover_url and cover_url.startswith('//'):
                cover_url = 'https:' + cover_url
            elif cover_url and cover_url.startswith('/'):
                base = re.match(r'(https?://[^/]+)', game_url)
                if base:
                    cover_url = base.group(1) + cover_url

            # ---- 简介 ----
            intro = ''
            for tag in soup2.find_all(['div', 'section', 'p', 'article']):
                text = tag.get_text(strip=True)
                if ('简介' in text or '介绍' in text or '描述' in text) and 20 < len(text) < 2000:
                    for marker in ['游戏简介', '游戏介绍', '剧情简介', '游戏描述', '简介', '介绍']:
                        if marker in text:
                            idx = text.index(marker) + len(marker)
                            intro = text[idx:].strip('：:： ')[:500]
                            break
                    if intro:
                        break
                    intro = text[:500]
                    break

            if not intro:
                # Meta description 作为后备
                meta_desc = soup2.select_one('meta[name="description"]')
                if meta_desc:
                    intro_text = meta_desc.get('content', '')
                    if intro_text and len(intro_text) > 20:
                        intro = intro_text[:500]

            if not intro:
                # 最后尝试找页面上任何有意义的文本
                for tag in soup2.find_all(['p', 'div']):
                    text = tag.get_text(strip=True)
                    if 50 < len(text) < 500 and '。' in text:
                        intro = text[:500]
                        break

            # ---- 标签 ----
            tags = []
            exclude_words = ['补丁', '修改器', '攻略', '存档', 'MOD', 'mod', '汉化',
                             '下载', '全DLC', '全', '位置', '地图', '装备', '版本', '新闻',
                             '骑士', '战士', '盗贼', '预言', '剑士', '法师', '无用', '无用之人',
                             '武士', '密使', '观星者', '囚犯', '勇者', '英雄', '恶兆',
                             '职业', '流派', '加点', '全流程', '收集', '成就']
            # 找游戏信息区域
            info_area = soup2.select_one('.game-info, .game-attr, .info-box, .game-meta, .g-info, .detail-info')
            source_elems = info_area.select('a, span.tag, span.type, .label') if info_area else []
            if not source_elems:
                source_elems = (soup2.select('.tag a, .type a, .info-tag a')
                                or soup2.select('[class*="tag"] a, [class*="type"] a'))

            for t in source_elems[:20]:
                tag_text = t.get_text(strip=True)
                if (tag_text and 2 <= len(tag_text) <= 6
                        and not any(w in tag_text for w in exclude_words)
                        and re.match(r'^[\u4e00-\u9fff\w]+$', tag_text)):
                    tags.append(tag_text)
            tags = list(dict.fromkeys(tags))[:6]

            # ---- 发售日期 ----
            release_date = None
            for de in soup2.select('[class*="date"], [class*="time"], .game-date, .release'):
                date_text = de.get_text(strip=True)
                match = re.search(r'(\d{4}).*?(\d{1,2}).*?(\d{1,2})', date_text)
                if match:
                    release_date = f'{match.group(1)}-{int(match.group(2)):02d}-{int(match.group(3)):02d}'
                    break

            return {
                'title': game_title,
                'tags': tags,
                'intro': intro,
                'cover_image_url': cover_url,
                'release_date': release_date,
                'purchase_link': game_url,
            }
        except Exception:
            return {}

    def merge_data(self, search_name, steam, douban, youxia=None, doyo=None, threedm=None):
        """合并所有来源的数据，豆瓣中文信息优先"""
        youxia = youxia or {}
        doyo = doyo or {}
        threedm = threedm or {}

        title = douban.get('douban_title') or youxia.get('title') or steam.get('title', search_name)
        rating = douban.get('douban_rating') or 0
        tags = list(dict.fromkeys(
            douban.get('tags', []) +
            steam.get('tags', []) +
            youxia.get('tags', []) +
            doyo.get('tags', []) +
            threedm.get('tags', [])
        ))
        # 简介：豆瓣优先，Steam/游侠/逗游/3DM 补充
        intro = (douban.get('douban_intro', '')
                 or steam.get('official_intro', '')
                 or youxia.get('intro', '')
                 or doyo.get('intro', '')
                 or threedm.get('intro', ''))

        # 封面：Steam 优先，游侠/逗游/3DM 补充
        cover = (steam.get('cover_image_url', '')
                 or youxia.get('cover_image_url', '')
                 or doyo.get('cover_image_url', '')
                 or threedm.get('cover_image_url', ''))

        # 购买链接
        purchase = steam.get('purchase_link', '') or youxia.get('purchase_link', '')

        return {
            'title': title,
            'rating': float(rating) if rating else 0,
            'official_intro': intro,
            'cover_image_url': cover,
            'purchase_link': purchase,
            'release_date': steam.get('release_date') or youxia.get('release_date'),
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
            for key in ['official_intro', 'purchase_link']:
                if data.get(key):
                    setattr(game, key, data[key])
            # 日期只保留 YYYY-MM-DD 格式
            rd = data.get('release_date')
            if rd and re.match(r'^\d{4}-\d{2}-\d{2}$', str(rd)):
                game.release_date = rd
            game.rating = data.get('rating', game.rating)
            game.save()
            self.stdout.write(self.style.SUCCESS(f'  已更新: {title}'))
        else:
            rd = data.get('release_date')
            if not rd or not re.match(r'^\d{4}-\d{2}-\d{2}$', str(rd)):
                rd = None
            game = Game.objects.create(
                title=title,
                rating=data.get('rating', 0),
                official_intro=data.get('official_intro', ''),
                purchase_link=data.get('purchase_link', ''),
                release_date=rd,
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
        if cover_url and (not game.cover_image or update):
            try:
                self.stdout.write(f'  下载封面: {cover_url[:80]}...')
                img_headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.ali213.net/'}
                resp = requests.get(cover_url, headers=img_headers, timeout=30)
                if resp.status_code == 200:
                    ext = cover_url.split('.')[-1].split('?')[0] or 'jpg'
                    if ext not in ('jpg', 'jpeg', 'png', 'webp'):
                        ext = 'jpg'
                    safe_title = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]+', '_', title)
                    filename = f"{game.id}_{safe_title}.{ext}"
                    game.cover_image.save(filename, ContentFile(resp.content), save=True)
                    self.stdout.write(f'  封面已下载')
                else:
                    self.stdout.write(self.style.WARNING(f'  封面下载失败: HTTP {resp.status_code}'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  封面下载失败: {e}'))

        self.stdout.write(self.style.SUCCESS(f'  标签: {", ".join(data.get("tags", []))}'))
