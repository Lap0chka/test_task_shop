from typing import List

from django.contrib import admin
from django.db.models import Model
from django.http import HttpResponse
from django.utils.html import format_html
from django.utils.safestring import SafeString

from .models import Order, OrderItem, ShippingAddress


class ShippingAddressAdmin(admin.ModelAdmin):
    """
    Admin interface for the Shipping Address model.

    Attributes:
        list_display (tuple): Fields to display in the list view.
        empty_value_display (str): Placeholder for empty values.
        list_display_links (tuple): Fields that link to the detail view.
        list_filter (tuple): Fields to filter the list view by.
    """

    list_display = ("full_name_bold", "user", "email", "country", "city", "zip")
    empty_value_display = "-empty-"
    list_display_links = ("full_name_bold",)
    list_filter = ("user", "country", "city")

    @admin.display(description="Full Name", empty_value="Noname")
    def full_name_bold(self, obj: Model) -> SafeString:
        """
        Displays the full name in bold HTML format.
        """
        return format_html("<b style='font-weight: bold;'>{}</b>", obj.full_name)


class OrderItemInline(admin.TabularInline):
    """
    Inline configuration for Order Item in the admin interface.
    """

    model = OrderItem
    extra = 0

    def get_readonly_fields(
        self, request: HttpResponse, obj: Model = None
    ) -> List[str]:
        """
        Specifies fields to set as readonly if the object exists.
        """
        if obj:
            return ["price", "product", "quantity", "user"]
        return super().get_readonly_fields(request, obj)


class OrderAdmin(admin.ModelAdmin):
    """
    Admin interface for the Order model.
    """

    list_display = [
        "id",
        "user",
        "shipping_address",
        "amount",
        "created",
        "updated",
        "is_paid",
        "discount",
    ]
    list_filter = [
        "is_paid",
        "updated",
        "created",
    ]
    inlines = [OrderItemInline]
    list_per_page = 15
    list_display_links = ["id", "user"]


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress, ShippingAddressAdmin)
