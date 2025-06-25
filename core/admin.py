from django.contrib import admin
from django.conf import settings

# Customize the admin site
admin.site.site_header = f"Gemstone Admin ({settings.ENVIRONMENT})"
admin.site.site_title = "Gemstone"
admin.site.index_title = "Gemstone Administration"