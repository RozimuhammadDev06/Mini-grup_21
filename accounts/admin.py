from django.apps import apps
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    AuditLog,
    Cart,
    CartItem,
    Category,
    Order,
    OrderItem,
    OrderStatusHistory,
    Payment,
    PlatformPromoCode,
    Product,
    ProductImage,
    ProductVariant,
    Review,
    ReviewImage,
    SellerDiscount,
    Stock,
    User,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("-created_at",)
    list_display = ("phone", "email", "first_name", "last_name", "role", "customer_type", "is_active")
    list_filter = ("role", "customer_type", "is_active", "is_phone_verified")
    search_fields = ("phone", "email", "first_name", "last_name")
    readonly_fields = ("last_login", "date_joined", "created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("Личные данные", {"fields": ("first_name", "last_name", "email", "avatar_url", "language", "is_phone_verified")}),
        ("Роль", {"fields": ("role", "customer_type")}),
        ("Права", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Даты", {"fields": ("last_login", "date_joined", "created_at", "updated_at")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("phone", "email", "role", "customer_type", "password1", "password2")}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name_ru", "name_uz", "parent", "sort_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name_ru", "name_uz", "slug")
    prepopulated_fields = {"slug": ("name_ru",)}


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name_ru", "sku", "category", "brand", "is_hit", "is_new", "is_active")
    list_filter = ("is_active", "is_hit", "is_new", "category", "brand")
    search_fields = ("name_ru", "name_uz", "sku", "barcode")
    prepopulated_fields = {"slug": ("name_ru",)}
    inlines = [ProductVariantInline, ProductImageInline]


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("variant", "warehouse", "quantity", "reserved_quantity", "low_stock_threshold")
    list_filter = ("warehouse",)
    search_fields = ("variant__sku", "variant__product__name_ru")


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "session_id", "customer_type", "updated_at")
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "user", "customer_type", "status", "total", "delivery_method", "created_at")
    list_filter = ("status", "customer_type", "delivery_method", "created_at")
    search_fields = ("order_number", "user__phone", "guest_phone", "guest_name")
    inlines = [OrderItemInline, OrderStatusHistoryInline, PaymentInline]


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 0


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "status", "is_verified_purchase", "created_at")
    list_filter = ("status", "rating", "is_verified_purchase")
    search_fields = ("product__name_ru", "user__phone", "body")
    inlines = [ReviewImageInline]


@admin.register(SellerDiscount)
class SellerDiscountAdmin(admin.ModelAdmin):
    list_display = ("name", "discount_type", "value", "starts_at", "ends_at", "is_active")
    list_filter = ("discount_type", "is_active")
    search_fields = ("name",)


@admin.register(PlatformPromoCode)
class PlatformPromoCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_type", "value", "used_count", "max_uses", "valid_to", "is_active")
    list_filter = ("discount_type", "is_active")
    search_fields = ("code",)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "action", "entity_type", "entity_id")
    list_filter = ("action", "entity_type")
    readonly_fields = [f.name for f in AuditLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


for model in apps.get_app_config("accounts").get_models():
    if not admin.site.is_registered(model):
        admin.site.register(model)
