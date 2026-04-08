from django.contrib import admin
from .models import Ticket, TicketComment


class TicketCommentInline(admin.StackedInline):
    model = TicketComment
    extra = 0


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("subject", "status", "priority", "channel", "contact", "assigned_to", "created_at")
    list_filter = ("status", "priority", "channel")
    search_fields = ("subject", "description")
    inlines = [TicketCommentInline]
    date_hierarchy = "created_at"
