from django.contrib import admin
from .models import Languages, Board


class BoardAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'processor',
                    'slug')


admin.site.register(Board, BoardAdmin)


admin.site.register(Languages)