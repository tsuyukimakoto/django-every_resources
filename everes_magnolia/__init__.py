#from everes_core import INFO_DICT
from models import Bookmark

INFO_DICT = dict(date_field='published_from', month_format='%m')
APP_DICT = INFO_DICT.copy()
APP_DICT.update(queryset=Bookmark.public_objects.all())
USE_SLUG = False
