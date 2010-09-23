#from everes_core import INFO_DICT
from models import Project

INFO_DICT = dict(date_field='published_from', month_format='%m')
APP_DICT = INFO_DICT.copy()
APP_DICT.update(queryset=Project.public_objects.all())
USE_SLUG = True
