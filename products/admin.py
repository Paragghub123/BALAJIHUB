from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import ProductUserDetail, ProductDetail
from django.db.models import Sum

class ProductUserDetailAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'total_price')
    readonly_fields = ('total_price',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Superusers see everything
        return qs.filter(user=request.user)

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.user == request.user

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.user == request.user

    def has_view_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj.user == request.user

    def has_add_permission(self, request):
        return True  # Or restrict based on your needs

admin.site.register(ProductUserDetail, ProductUserDetailAdmin)

class ProductDetailInline(admin.TabularInline):
    model = ProductUserDetail
    extra = 1  # No extra empty forms
    fields = ('product', 'quantity', 'total_price')

class CustomUserAdmin(BaseUserAdmin):
    inlines = [ProductDetailInline]
    list_display = BaseUserAdmin.list_display + ('gross_order_price',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(id=request.user.id)

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or obj == request.user

    def has_view_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser  # Only superusers can add users

    # Custom field to display gross order price
    def gross_order_price(self, obj):
        total = obj.user_product_detail.aggregate(total=Sum('total_price'))['total'] or 0
        return f"{total:.2f} €"
    gross_order_price.short_description = "Gross Order Price"
    gross_order_price.admin_order_field = 'user_product_detail__total_price'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(ProductDetail)
class ProductDetailAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')