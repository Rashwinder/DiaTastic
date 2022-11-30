from django.contrib import admin
from . import models

admin.site.register(models.User)
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'first_name', 'email']