#from everes_core import INFO_DICT
from models import Release

INFO_DICT = dict(date_field='published_from', month_format='%m')
APP_DICT = INFO_DICT.copy()
APP_DICT.update(queryset=Release.public_objects.all())
USE_SLUG = True
