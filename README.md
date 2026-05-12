# 🎮 游戏推荐网站

基于 Django REST + Vue 3 的个人游戏推荐网站，支持从 Steam 和豆瓣爬取游戏信息。

## 环境要求

- Python 3.10+
- Node.js 18+
- npm 9+

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/theshisanyi/shisanyi.git
cd shisanyi
```

### 2. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
```

### 3. 创建管理员账号

```bash
python manage.py createsuperuser
```

### 4. 安装前端依赖

```bash
cd ../frontend
npm install
```

### 5. 启动项目

打开两个终端：

**终端 1 - 启动后端：**

```bash
cd backend
python manage.py runserver
```

**终端 2 - 启动前端：**

```bash
cd frontend
npm run dev
```

### 6. 访问

| 地址 | 说明 |
|------|------|
| `http://localhost:5173` | 网站首页 |
| `http://localhost:8000/admin` | 管理后台 |

## 爬取游戏数据

> **注意**：Steam 爬取需要直连 `store.steampowered.com`。公司网络可能拦截，此时 Steam 会超时（豆瓣数据仍可获取）。可通过代理/VPN 或在家庭网络环境使用。

网站刚搭建时没有数据，需要通过爬虫获取游戏信息：

```bash
cd backend

# 预览数据（不入库）
python manage.py scrape_games "艾尔登法环" "黑神话悟空" --dry-run

# 确认无误后入库
python manage.py scrape_games "艾尔登法环" "黑神话悟空"

# 批量爬取
python manage.py scrape_games "艾尔登法环" "黑神话悟空" "塞尔达传说" "巫师3"
```

爬虫会自动从 Steam 获取封面图、官方简介、标签，从豆瓣获取中文名称和评分。

如果 Steam 网络不通，也可以直接通过管理后台手动添加游戏。

## 管理后台操作

登录 `http://localhost:8000/admin` 后可以：

- **添加/编辑游戏**：手动录入游戏信息、上传封面、撰写评测
- **管理分类标签**：增删游戏分类
- **设置热门游戏**：勾选 `is_hot` + 设置 `sort_weight` → 出现在首页轮播
- **配置相似推荐**：在 Game 编辑页底部关联相似游戏

### 撰写评测

评测字段支持 HTML 格式，例如：

```html
<h3>总体评价</h3>
<p>这款游戏的世界观令人惊叹...</p>
<h4>优点</h4>
<ul>
  <li>出色的美术设计</li>
</ul>
<h4>缺点</h4>
<ul>
  <li>后期内容略显重复</li>
</ul>
```

## 项目结构

```
├── backend/                    # Django REST API
│   ├── config/                 # Django 配置
│   ├── games/                  # 游戏应用
│   │   ├── models.py           # 数据模型
│   │   ├── admin.py            # 管理后台配置
│   │   ├── serializers.py      # API 序列化
│   │   ├── views.py            # API 视图
│   │   └── management/commands/
│   │       └── scrape_games.py # 爬虫命令
│   ├── media/                  # 上传/爬取的图片
│   └── requirements.txt
├── frontend/                   # Vue 3 SPA
│   ├── src/
│   │   ├── views/
│   │   │   ├── HomePage.vue    # 首页（轮播+卡片）
│   │   │   └── GameDetail.vue  # 详情页（模糊背景+相似推荐）
│   │   └── components/
│   │       ├── HotCarousel.vue
│   │       ├── SortBar.vue
│   │       ├── GameCard.vue
│   │       └── SimilarGamesSidebar.vue
│   └── vite.config.js
└── README.md
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/games/` | 游戏列表，支持 `?ordering=-rating&category=rpg` |
| GET | `/api/games/?is_hot=true` | 热门游戏（首页轮播 Top 5） |
| GET | `/api/games/{id}/` | 游戏详情（含相似推荐） |
| GET | `/api/categories/` | 分类列表 |

## 部署到服务器

### 后端

```bash
cd backend
pip install gunicorn
gunicorn config.wsgi:application -b 127.0.0.1:8000
```

### 前端

```bash
cd frontend
npm run build
# 将 dist/ 目录部署到 Nginx 静态文件目录
```

### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /media/ {
        alias /path/to/backend/media/;
    }

    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

## 技术栈

- **后端**：Django 5.1 + Django REST Framework 3.15
- **前端**：Vue 3.4 + Vite 5 + Vue Router 4 + Pinia 2 + Axios
- **爬虫**：requests + BeautifulSoup4 + lxml
- **数据库**：SQLite（开发）/ PostgreSQL（生产推荐）
