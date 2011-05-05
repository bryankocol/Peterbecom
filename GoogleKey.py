import os
from Globals import package_home

if os.path.isfile(os.path.expanduser('~/.googlemaps_api.key')):
    GOOGLEMAPS_API_KEY = open(os.path.expanduser('~/.googlemaps_api.key')).read()
elif os.path.isfile(os.path.join(package_home(globals()), 'googlemaps_api.key')):
    GOOGLEMAPS_API_KEY = open(os.path.join(package_home(globals()), 'googlemaps_api.key')).read()
elif os.environ.get('GOOGLEMAPS_API_KEY', None):
    GOOGLEMAPS_API_KEY = os.environ.get('GOOGLEMAPS_API_KEY')
else:
    raise ImportError, "Can't find googlemaps API key"