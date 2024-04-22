from django.contrib import admin

# Register your models here.
from . models import Author, Story, Agency
admin.site.register(Author)
admin.site.register(Story)
admin.site.register(Agency)