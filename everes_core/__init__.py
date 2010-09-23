from models import ContentsMeta

INFO_DICT = dict(queryset=ContentsMeta.public_objects.all(), date_field='published_from', month_format='%m')
APP_DICT = INFO_DICT.copy()

USE_SLUG  = False
