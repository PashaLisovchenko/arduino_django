from django.contrib import admin
from .models import Languages, Board, FamilyProcessor, Processor, IDE, Category


class ProcessorAdmin(admin.ModelAdmin):
    list_display = ('name', 'family')


class BoardAdmin(admin.ModelAdmin):
    list_filter =  ['programming_languages', 'processor__family']
    list_display = ('id', 'name', 'slug')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Category, CategoryAdmin)
admin.site.register(Processor, ProcessorAdmin)
admin.site.register(Board, BoardAdmin)

admin.site.register(Languages)
admin.site.register(FamilyProcessor)
admin.site.register(IDE)
