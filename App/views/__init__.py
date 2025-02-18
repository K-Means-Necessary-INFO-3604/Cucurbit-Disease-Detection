# blue prints are imported 
# explicitly instead of using *
from .index import index_views
from .auth import auth_views


views = [index_views, auth_views] 
# blueprints must be added to this list