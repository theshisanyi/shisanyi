import os, sys
sys.path.insert(0, '.')
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
import django
django.setup()
from games.models import Game
for g in Game.objects.all():
    url = g.cover_image.url if g.cover_image else 'NONE'
    print("title:", g.title)
    print("cover:", g.cover_image)
    print("url:", url)
    print()
