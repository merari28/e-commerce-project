from django.contrib import admin
from .models import Product, ReviewRating, Variation, ProductGallery


class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'created_date', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    inlines = [ProductGalleryInline]


class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value', 'is_active')


class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'status', 'created_at')
    list_filter = ('status', 'rating', 'created_at')
    search_fields = ('product__product_name', 'user__email', 'review')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating, ReviewRatingAdmin)