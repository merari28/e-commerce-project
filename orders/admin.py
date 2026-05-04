from django.contrib import admin
from .models import Order, Payment, OrderProduct
from django.utils.safestring import mark_safe


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 0

    readonly_fields = (
        'payment',
        'user',
        'product',
        'get_variations',
        'quantity',
        'product_price',
        'ordered',
    )

    fields = (
        'payment',
        'user',
        'product',
        'get_variations',
        'quantity',
        'product_price',
        'ordered',
    )

    def get_variations(self, obj):
        return mark_safe("".join([
            f'<span style="background:#00c853;color:white;padding:3px 8px;border-radius:5px;margin-right:5px;">{v.variation_category}: {v.variation_value}</span>'
            for v in obj.variation.all()
        ])) if obj else ""

    get_variations.short_description = "Variaciones seleccionadas"


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number',
        'full_name',
        'email',
        'phone',
        'country',
        'city',
        'order_total',
        'status',
        'created_at'
    )
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'full_name', 'email', 'phone')
    list_per_page = 20
    inlines = [OrderProductInline]


class OrderProductAdmin(admin.ModelAdmin):

    readonly_fields = ('get_variations',)

    fields = (
        'order',
        'payment',
        'user',
        'product',
        'get_variations',
        'quantity',
        'product_price',
        'ordered',
    )

    def get_variations(self, obj):
        return mark_safe("".join([
            f'<span style="background:#00c853;color:white;padding:3px 8px;border-radius:5px;margin-right:5px;">{v.variation_category}: {v.variation_value}</span>'
            for v in obj.variation.all()
        ])) if obj else ""

    get_variations.short_description = "Variaciones seleccionadas"


admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(OrderProduct, OrderProductAdmin)