from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Contact


class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'email', 'info', 'phone',)
    list_editable = ('info',)
    list_display_links = ('name',)
    list_per_page = 10
    search_fields = ('name', 'info', 'gender')
    list_filter = ('gender', 'date_added')


admin.site.register(Contact, ContactAdmin)
admin.site.unregister(Group)
