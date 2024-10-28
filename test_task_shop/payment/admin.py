import csv
import datetime
from typing import List, Any
from django.contrib import admin
from django.http import HttpResponse, HttpRequest
from django.db.models import Model, QuerySet
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.contrib.admin import ModelAdmin
from .models import Order, OrderItem, ShippingAddress


def export_paid_to_csv(modeladmin: Any, request: HttpRequest, queryset: Any) -> HttpResponse:
    """
    Exports objects from the given queryset with a `True` value for `is_paid` to a CSV file.
    """
    opts = modeladmin.model._meta
    content_disposition = f"attachment; filename=Paid{opts.verbose_name}.csv"
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = content_disposition
    writer = csv.writer(response)

    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    writer.writerow([field.verbose_name for field in fields])

    for obj in queryset:
        if not getattr(obj, "is_paid"):
            continue
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime("%d/%m/%Y")
            data_row.append(value)
        writer.writerow(data_row)
    return response


export_paid_to_csv.short_description = "Export Paid to CSV"


def export_not_paid_to_csv(modeladmin: ModelAdmin, request: HttpResponse, queryset: QuerySet[Model]) -> HttpResponse:
    """
    Exports objects from the given queryset with a `False` value for `is_paid` to a CSV file.
    """
    opts = modeladmin.model._meta
    content_disposition = f"attachment; filename=NotPaid{opts.verbose_name}.csv"
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = content_disposition
    writer = csv.writer(response)

    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    writer.writerow([field.verbose_name for field in fields])

    for obj in queryset:
        if getattr(obj, "is_paid"):
            continue
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime("%d/%m/%Y")
            data_row.append(value)
        writer.writerow(data_row)
    return response


export_not_paid_to_csv.short_description = "Export Not Paid to CSV"


def order_pdf(obj: Model) -> SafeString:
    """
    Generates a link to the PDF invoice for a given order object.
    """
    url = reverse("payment:admin_order_pdf", args=[obj.id])
    return format_html(f'<a href="{url}">PDF</a>')


order_pdf.short_description = "Invoice"


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

    def get_readonly_fields(self, request: HttpResponse, obj: Model = None) -> List[str]:
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
        "id", "user", "shipping_address", "amount", "created", "updated", "is_paid", "discount", order_pdf,
    ]
    list_filter = [
        "is_paid", "updated", "created",
    ]
    inlines = [OrderItemInline]
    list_per_page = 15
    list_display_links = ["id", "user"]
    actions = [export_paid_to_csv, export_not_paid_to_csv]


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress, ShippingAddressAdmin)
