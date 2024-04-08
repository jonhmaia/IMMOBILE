from django.contrib import admin
from . import models
class ImmobileImageInlineAdmin(admin.TabularInline):
    model = models.ImmobileImage
    extra = 0

class ImmobileAdmin(admin.ModelAdmin):
    inlines = [ImmobileImageInlineAdmin]

admin.site.register(models.Immobile, ImmobileAdmin)
admin.site.register(models.Client)
admin.site.register(models.RegisterLocation)
