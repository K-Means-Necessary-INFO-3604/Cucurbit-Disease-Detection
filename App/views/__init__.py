# blue prints are imported 
# explicitly instead of using *
from .index import index_views
from .auth import auth_views
from .upload import upload_views

views = [index_views, auth_views, upload_views] 
# blueprints must be added to this list