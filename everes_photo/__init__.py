#from everes_core import INFO_DICT
from models import Shot

INFO_DICT = dict(date_field='published_from', month_format='%m')
APP_DICT = INFO_DICT.copy()
APP_DICT.update(queryset=Shot.public_objects.all())
USE_SLUG = False
