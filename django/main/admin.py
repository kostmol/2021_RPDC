from django.contrib import admin
from .models import *

# app
# admin.site.register(Author)
admin.site.register(AppUser)
admin.site.register(Papers)
admin.site.register(AuthorScopus)

# api
admin.site.register(ScopusAuthor)
admin.site.register(ScopusPaper)
admin.site.register(ScopusPaperAuthor)