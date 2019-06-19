from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Message


class ContactAdmin(admin.ModelAdmin):
    list_display = ('owner', 'date', 'content', 'toxic_ratio', 'severe_ratio',
                    'obscene_ratio', 'threat_ratio', 'insult_ratio', 'hate_ratio', 'toxic_comment')
    list_editable = ('content', 'toxic_comment')
    list_display_links = ('owner',)
    list_per_page = 10
    search_fields = ('owner', 'toxic_ratio', 'date')
    list_filter = ('owner', 'date')


admin.site.register(Message, ContactAdmin)
# admin.site.unregister(Group)
