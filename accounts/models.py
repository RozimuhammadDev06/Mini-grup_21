from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

from .managers import UserManager


# =====================================================================
# ENUMS
# =====================================================================

class UserRole(models.TextChoices):
    CUSTOMER = "customer", "Покупатель"
    WHOLESALE_CUSTOMER = "wholesale_customer", "Оптовый покупатель"
    MANAGER = "manager", "Менеджер"
    WAREHOUSE_WORKER = "warehouse_worker", "Складской работник"
    ADMIN = "admin", "Администратор"


class CustomerType(models.TextChoices):
    RETAIL = "retail", "Розница"
    WHOLESALE = "wholesale", "Опт"


class OrderStatus(models.TextChoices):
    NEW = "new", "Новый"
    CONFIRMED = "confirmed", "Подтверждён"
    PACKING = "packing", "Сборка"
    SHIPPED = "shipped", "Отгружен"
    DELIVERED = "delivered", "Доставили"
    CANCELLED = "cancelled", "Отменён"
    RETURNED = "returned", "Возврат"


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Ожидает оплаты"
    PAID = "paid", "Оплачен"
    FAILED = "failed", "Ошибка"
    REFUNDED = "refunded", "Возвращён"
    PARTIALLY_REFUNDED = "partially_refunded", "Частичный возврат"


class PaymentMethod(models.TextChoices):
    CASH = "cash", "Наличные"
    CARD_TRANSFER = "card_transfer", "Перевод на карту"
    CLICK = "click", "Click"
    PAYME = "payme", "Payme"
    UZUM_PAY = "uzum_pay", "Uzum Pay"
    BANK_INVOICE = "bank_invoice", "Счёт для юрлица"


class DeliveryMethod(models.TextChoices):
    PICKUP = "pickup", "Самовывоз"
    COURIER = "courier", "Курьер"
    COMPANY_TRUCK = "company_truck", "Доставка машиной компании"


class StockMovementType(models.TextChoices):
    INCOMING = "incoming", "Приход"
    OUTGOING = "outgoing", "Расход"
    RESERVATION = "reservation", "Резерв"
    RELEASE = "release", "Снятие резерва"
    ADJUSTMENT = "adjustment", "Корректировка"
    RETURN_IN = "return_in", "Возврат на склад"


class DiscountValueType(models.TextChoices):
    PERCENT = "percent", "Процент (%)"
    FIXED = "fixed", "Фиксированная сумма (UZS)"


class ReviewStatus(models.TextChoices):
    PENDING = "pending", "На модерации"
    APPROVED = "approved", "Одобрен"
    REJECTED = "rejected", "Отклонён"


class ReturnStatus(models.TextChoices):
    REQUESTED = "requested", "Запрошен"
    APPROVED = "approved", "Одобрен"
    REJECTED = "rejected", "Отклонён"
    RECEIVED = "received", "Получен на складе"
    REFUNDED = "refunded", "Возвращены деньги"


class PriceType(models.TextChoices):
    RETAIL = "retail", "Розница"
    WHOLESALE = "wholesale", "Опт"


# =====================================================================
# БАЗОВЫЕ КЛАССЫ
# =====================================================================

class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class TimestampedUpdatedModel(TimestampedModel):
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# =====================================================================
# ACCOUNTS
# =====================================================================

class User(AbstractUser):
    """Кастомный пользователь. В settings: AUTH_USER_MODEL = 'accounts.User'."""

    username = None  # логин - телефон
    phone = models.CharField("Телефон", max_length=20, unique=True, help_text="Формат +998XXXXXXXXX")
    email = models.EmailField("Email", unique=True, null=True, blank=True)
    role = models.CharField(max_length=32, choices=UserRole.choices, default=UserRole.CUSTOMER)
    customer_type = models.CharField(max_length=16, choices=CustomerType.choices, default=CustomerType.RETAIL)
    avatar_url = models.URLField("Фото профиля", max_length=500, blank=True)
    language = models.CharField(max_length=5, default="uz")
    is_phone_verified = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["customer_type"]),
        ]


class Company(TimestampedModel):
    name = models.CharField(max_length=255)
    inn = models.CharField("ИНН / STIR", max_length=20, unique=True, null=True, blank=True)
    bank_account = models.CharField(max_length=50, blank=True)
    bank_name = models.CharField(max_length=255, blank=True)
    legal_address = models.TextField(blank=True)
    contact_person = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="contact_for_companies"
    )
    credit_limit = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    payment_term_days = models.PositiveIntegerField(default=0)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class CompanyMember(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="company_memberships")
    position = models.CharField(max_length=100, blank=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        unique_together = ("company", "user")


class Address(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    region = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True)
    street = models.CharField(max_length=255)
    house = models.CharField(max_length=50, blank=True)
    apartment = models.CharField(max_length=50, blank=True)
    entrance = models.CharField(max_length=20, blank=True)
    floor = models.CharField(max_length=20, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    comment = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)


class RefreshToken(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="refresh_tokens")
    token_hash = models.CharField(max_length=255)
    user_agent = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)


class OtpCode(TimestampedModel):
    phone = models.CharField(max_length=20, db_index=True)
    code_hash = models.CharField(max_length=255)
    attempts = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)


# =====================================================================
# CATALOG
# =====================================================================

class Category(TimestampedModel):
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="children"
    )
    name_uz = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    description_ru = models.TextField(blank=True)
    image_url = models.URLField(max_length=500, blank=True)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name_ru"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name_ru


class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    logo_url = models.URLField(max_length=500, blank=True)
    country = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Unit(models.Model):
    code = models.CharField(max_length=20, unique=True, help_text="шт, м, м2, м3, кг, т, л, мешок, рулон, упак")
    name_ru = models.CharField(max_length=100)
    name_uz = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.code


class Supplier(TimestampedModel):
    name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    inn = models.CharField(max_length=20, blank=True)
    payment_term_days = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Product(TimestampedUpdatedModel):
    sku = models.CharField(max_length=64, unique=True)
    barcode = models.CharField(max_length=64, unique=True, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    brand = models.ForeignKey(Brand, null=True, blank=True, on_delete=models.SET_NULL, related_name="products")
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, related_name="products")
    name_uz = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    short_description = models.CharField(max_length=500, blank=True)
    description_ru = models.TextField(blank=True)
    description_uz = models.TextField(blank=True)
    specs = models.JSONField("Характеристики (свободная форма)", null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    length_cm = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    width_cm = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    height_cm = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    warranty_months = models.PositiveIntegerField(default=0)
    is_hit = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.CharField(max_length=500, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["is_active", "category"]),
            models.Index(fields=["name_ru"]),
        ]

    def __str__(self):
        return self.name_ru


class ProductVariant(TimestampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    sku = models.CharField(max_length=64, unique=True)
    barcode = models.CharField(max_length=64, unique=True, null=True, blank=True)
    name_suffix = models.CharField(max_length=255, blank=True, help_text="Например: 50 кг, 2.5 мм, черный")
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product} {self.name_suffix}".strip()


class Attribute(models.Model):
    class ValueType(models.TextChoices):
        STRING = "string", "Строка"
        NUMBER = "number", "Число"
        BOOLEAN = "boolean", "Да/Нет"
        ENUM = "enum", "Список значений"

    code = models.CharField(max_length=64, unique=True, help_text="color, size, material, voltage, power_w")
    name_ru = models.CharField(max_length=255)
    name_uz = models.CharField(max_length=255, blank=True)
    value_type = models.CharField(max_length=20, choices=ValueType.choices)
    unit = models.ForeignKey(Unit, null=True, blank=True, on_delete=models.SET_NULL, related_name="attributes")
    is_filterable = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.name_ru


class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="values")
    value_ru = models.CharField(max_length=255)
    value_uz = models.CharField(max_length=255, blank=True)
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.value_ru


class CategoryAttribute(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="category_attributes")
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="category_attributes")
    is_required = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)

    class Meta:
        unique_together = ("category", "attribute")


class ProductAttributeValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="attribute_values")
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="product_values")
    attribute_value = models.ForeignKey(
        AttributeValue, null=True, blank=True, on_delete=models.SET_NULL, related_name="product_values"
    )
    value_number = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    value_text = models.CharField(max_length=500, blank=True)
    value_bool = models.BooleanField(null=True, blank=True)

    class Meta:
        unique_together = ("product", "attribute")


class VariantAttributeValue(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name="attribute_values")
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="variant_values")
    attribute_value = models.ForeignKey(
        AttributeValue, null=True, blank=True, on_delete=models.SET_NULL, related_name="variant_values"
    )
    value_number = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    value_text = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("variant", "attribute")


class ProductImage(TimestampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    variant = models.ForeignKey(
        ProductVariant, null=True, blank=True, on_delete=models.SET_NULL, related_name="images"
    )
    image_url = models.URLField(max_length=500)
    alt_text = models.CharField(max_length=255, blank=True)
    sort_order = models.IntegerField(default=0)
    is_main = models.BooleanField(default=False)

    class Meta:
        ordering = ["sort_order"]


class ProductDocument(TimestampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=255, help_text="Сертификат, инструкция, паспорт")
    file_url = models.URLField(max_length=500)
    doc_type = models.CharField(max_length=50, blank=True)


class ProductSupplier(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="suppliers")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="products")
    supplier_sku = models.CharField(max_length=100, blank=True)
    purchase_price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="UZS")
    lead_time_days = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("product", "supplier")


# =====================================================================
# PRICING
# =====================================================================

class Price(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name="prices")
    price_type = models.CharField(max_length=16, choices=PriceType.choices, default=PriceType.RETAIL)
    price = models.DecimalField(max_digits=14, decimal_places=2, help_text="UZS")
    old_price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["variant", "price_type", "valid_from"])]


class WholesalePriceTier(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name="wholesale_tiers")
    min_qty = models.DecimalField(max_digits=12, decimal_places=3)
    price = models.DecimalField(max_digits=14, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("variant", "min_qty")
        ordering = ["min_qty"]


# =====================================================================
# INVENTORY
# =====================================================================

class Warehouse(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Stock(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name="stocks")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="stocks")
    quantity = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    reserved_quantity = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    low_stock_threshold = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("variant", "warehouse")

    @property
    def available(self):
        return self.quantity - self.reserved_quantity


class StockMovement(TimestampedModel):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name="movements")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="movements")
    movement_type = models.CharField(max_length=20, choices=StockMovementType.choices)
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    reference_type = models.CharField(max_length=50, blank=True, help_text="order, purchase, return, manual")
    reference_id = models.PositiveIntegerField(null=True, blank=True)
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="stock_movements"
    )
    comment = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["variant", "warehouse"]),
            models.Index(fields=["reference_type", "reference_id"]),
        ]


class PurchaseOrder(TimestampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        SENT = "sent", "Отправлен"
        PARTIAL = "partial", "Частично получен"
        RECEIVED = "received", "Получен"
        CANCELLED = "cancelled", "Отменён"

    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="purchase_orders")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="purchase_orders")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    expected_at = models.DateTimeField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="purchase_orders"
    )


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, related_name="purchase_items")
    ordered_qty = models.DecimalField(max_digits=12, decimal_places=3)
    received_qty = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    unit_cost = models.DecimalField(max_digits=14, decimal_places=2)


# =====================================================================
# CART & WISHLIST
# =====================================================================

class Cart(TimestampedUpdatedModel):
    user = models.OneToOneField(
        User, null=True, blank=True, on_delete=models.CASCADE, related_name="cart"
    )
    session_id = models.CharField(max_length=64, unique=True, null=True, blank=True)
    customer_type = models.CharField(max_length=16, choices=CustomerType.choices, default=CustomerType.RETAIL)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.DecimalField(max_digits=12, decimal_places=3, default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("cart", "variant")


class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlisted_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")


# =====================================================================
# ORDERS
# =====================================================================

class DeliveryZone(models.Model):
    region = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True)
    base_fee = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    free_from_total = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    delivery_method = models.CharField(max_length=20, choices=DeliveryMethod.choices)
    is_active = models.BooleanField(default=True)


class Order(TimestampedUpdatedModel):
    order_number = models.CharField(max_length=20, unique=True, help_text="ЗК-000123")
    user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="orders"
    )
    company = models.ForeignKey(
        Company, null=True, blank=True, on_delete=models.SET_NULL, related_name="orders"
    )
    guest_name = models.CharField(max_length=255, blank=True)
    guest_phone = models.CharField(max_length=20, blank=True)
    customer_type = models.CharField(max_length=16, choices=CustomerType.choices, default=CustomerType.RETAIL)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.NEW)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2)
    discount_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=14, decimal_places=2)
    promo_code = models.ForeignKey(
        "PlatformPromoCode", null=True, blank=True, on_delete=models.SET_NULL, related_name="orders"
    )
    delivery_method = models.CharField(max_length=20, choices=DeliveryMethod.choices)
    delivery_address = models.ForeignKey(
        Address, null=True, blank=True, on_delete=models.SET_NULL, related_name="orders"
    )
    delivery_address_snapshot = models.JSONField("Адрес на момент заказа", null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    delivery_time_slot = models.CharField(max_length=50, blank=True)
    customer_comment = models.TextField(blank=True)
    manager = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="managed_orders"
    )
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancel_reason = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(
        ProductVariant, null=True, on_delete=models.SET_NULL, related_name="order_items"
    )
    product_name_snapshot = models.CharField(max_length=255)
    sku_snapshot = models.CharField(max_length=64)
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    unit_price = models.DecimalField(max_digits=14, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=14, decimal_places=2)


class OrderStatusHistory(TimestampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="status_history")
    from_status = models.CharField(max_length=20, choices=OrderStatus.choices, blank=True)
    to_status = models.CharField(max_length=20, choices=OrderStatus.choices)
    changed_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="order_status_changes"
    )
    comment = models.TextField(blank=True)


class Payment(TimestampedModel):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="payments")
    method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="UZS")
    provider_transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    provider_payload = models.JSONField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)


class Invoice(TimestampedModel):
    order = models.OneToOneField(Order, on_delete=models.PROTECT, related_name="invoice")
    invoice_number = models.CharField(max_length=50, unique=True)
    company = models.ForeignKey(
        Company, null=True, blank=True, on_delete=models.SET_NULL, related_name="invoices"
    )
    total = models.DecimalField(max_digits=14, decimal_places=2)
    due_date = models.DateField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    pdf_url = models.URLField(max_length=500, blank=True)


class Shipment(TimestampedModel):
    class Status(models.TextChoices):
        PLANNED = "planned", "Запланирована"
        IN_TRANSIT = "in_transit", "В пути"
        DELIVERED = "delivered", "Доставлена"
        FAILED = "failed", "Не доставлена"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="shipments")
    courier = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="shipments"
    )
    vehicle_number = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED)
    planned_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    recipient_name = models.CharField(max_length=255, blank=True)
    recipient_signature_url = models.URLField(max_length=500, blank=True)


class Return(TimestampedUpdatedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="returns")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="returns")
    status = models.CharField(max_length=20, choices=ReturnStatus.choices, default=ReturnStatus.REQUESTED)
    reason = models.TextField(blank=True)
    refund_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)


class ReturnItem(models.Model):
    return_request = models.ForeignKey(Return, on_delete=models.CASCADE, related_name="items")
    order_item = models.ForeignKey(OrderItem, on_delete=models.PROTECT, related_name="return_items")
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    condition = models.CharField(max_length=50, blank=True, help_text="new, opened, damaged")


# =====================================================================
# REVIEWS & QUESTIONS
# =====================================================================

class Review(TimestampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    order_item = models.ForeignKey(
        OrderItem, null=True, blank=True, on_delete=models.SET_NULL, related_name="reviews",
        help_text="Отзыв только от купившего",
    )
    rating = models.PositiveSmallIntegerField(help_text="1..5")
    pros = models.TextField(blank=True)
    cons = models.TextField(blank=True)
    body = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=ReviewStatus.choices, default=ReviewStatus.PENDING)
    is_verified_purchase = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=["product", "status"])]


class ReviewImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="images")
    image_url = models.URLField(max_length=500)


class ProductQuestion(TimestampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="questions")
    user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="product_questions"
    )
    question = models.TextField()
    answer = models.TextField(blank=True)
    answered_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="answered_questions"
    )
    is_published = models.BooleanField(default=False)
    answered_at = models.DateTimeField(null=True, blank=True)


# =====================================================================
# CORE
# =====================================================================

class Notification(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    type = models.CharField(max_length=50, help_text="order_status, promo, stock_back, price_drop")
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    payload = models.JSONField(null=True, blank=True)
    channel = models.CharField(max_length=20, blank=True, help_text="sms, telegram, email, push")
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["user", "is_read"])]


class StockSubscription(TimestampedModel):
    """Уведомить, когда товар появится в наличии."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stock_subscriptions")
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name="stock_subscriptions")
    notified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "variant")


class Banner(models.Model):
    title = models.CharField(max_length=255, blank=True)
    image_url = models.URLField(max_length=500)
    link_url = models.URLField(max_length=500, blank=True)
    position = models.CharField(max_length=50, blank=True, help_text="home_top, home_middle, category")
    sort_order = models.IntegerField(default=0)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)


class Setting(models.Model):
    key = models.CharField(max_length=100, primary_key=True)
    value = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="updated_settings"
    )


class AuditLog(models.Model):
    user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="audit_logs"
    )
    action = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=50, blank=True)
    entity_id = models.PositiveIntegerField(null=True, blank=True)
    diff = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["created_at"]),
        ]


# =====================================================================
# SELLER & PLATFORM DISCOUNTS (НОВЫЕ МОДЕЛИ СКИДОК)
# =====================================================================

class SellerDiscount(TimestampedUpdatedModel):
    """
    Скидка, предоставляемая продавцом на товары, категории или бренды.
    Поддерживает скидки в % и в фиксированных суммах UZS.
    """
    name = models.CharField("Название акции", max_length=255)
    discount_type = models.CharField(
        "Тип скидки",
        max_length=16,
        choices=DiscountValueType.choices,
        default=DiscountValueType.PERCENT
    )
    value = models.DecimalField(
        "Значение скидки",
        max_digits=14,
        decimal_places=2,
        help_text="Если процент — указывать от 1 до 100. Если сумма — в сумах (UZS)."
    )
    max_discount_amount = models.DecimalField(
        "Максимальная сумма скидки (UZS)",
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Ограничение для процентных скидок, чтобы скидка не превысила заданный лимит в сумах."
    )

    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.CASCADE,
                                related_name="seller_discounts")
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE,
                                 related_name="seller_discounts")
    brand = models.ForeignKey(Brand, null=True, blank=True, on_delete=models.CASCADE, related_name="seller_discounts")

    starts_at = models.DateTimeField("Дата начала")
    ends_at = models.DateTimeField("Дата окончания", null=True, blank=True)
    is_active = models.BooleanField("Активна", default=True)

    class Meta:
        verbose_name = "Скидка продавца"
        verbose_name_plural = "Скидки продавцов"

    def calculate_discount(self, base_price):
        """Расчет итоговой суммы скидки продавца в сумах."""
        if not self.is_active:
            return 0

        if self.discount_type == DiscountValueType.FIXED:
            return min(self.value, base_price)
        else:
            calculated = (base_price * self.value) / 100
            if self.max_discount_amount:
                calculated = min(calculated, self.max_discount_amount)
            return min(calculated, base_price)


class PlatformPromoCode(TimestampedUpdatedModel):
    """
    Промокод от платформы/сайта.
    Может быть процентным или в фиксированной сумме UZS.
    """
    code = models.CharField("Промокод", max_length=50, unique=True)
    discount_type = models.CharField(
        "Тип скидки",
        max_length=16,
        choices=DiscountValueType.choices,
        default=DiscountValueType.PERCENT
    )
    value = models.DecimalField(
        "Размер скидки",
        max_digits=14,
        decimal_places=2,
        help_text="Процент (1-100) или фиксированная сумма в сумах."
    )
    max_discount_amount = models.DecimalField(
        "Макс. скидка в сумах (для %)",
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True
    )
    min_order_total = models.DecimalField(
        "Мин. сумма заказа (UZS)",
        max_digits=14,
        decimal_places=2,
        default=0
    )

    max_uses = models.PositiveIntegerField("Всего применений", null=True, blank=True)
    used_count = models.PositiveIntegerField("Использовано раз", default=0)
    per_user_limit = models.PositiveIntegerField("Лимит на одного пользователя", default=1)

    allow_with_seller_discount = models.BooleanField(
        "Применять поверх скидки продавца",
        default=True,
        help_text="Если False, промокод применяется только к товарам без скидки продавца."
    )

    valid_from = models.DateTimeField("Действует с", null=True, blank=True)
    valid_to = models.DateTimeField("Действует до", null=True, blank=True)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Промокод платформы"
        verbose_name_plural = "Промокоды платформы"


class DiscountProtectionPolicy(TimestampedUpdatedModel):
    """
    Правила расчёта и защиты от нежелательного наслоения скидок.
    """
    name = models.CharField("Название правила", max_length=100, default="Стандартная защита скидок")
    max_combined_discount_percent = models.DecimalField(
        "Максимальный суммарный % скидки",
        max_digits=5,
        decimal_places=2,
        default=70.00,
        help_text="Суммарная скидка (продавец + промокод) не может превышать этот % от первоначальной цены."
    )
    min_price_margin_percent = models.DecimalField(
        "Минимальная цена товара после скидок (% от розницы)",
        max_digits=5,
        decimal_places=2,
        default=30.00,
        help_text="Итоговая цена товара после всех скидок не может быть ниже 30% от оригинальной цены."
    )
    apply_promo_on_discounted_price = models.BooleanField(
        "Считать промокод от уже уцененной цены продавца",
        default=True,
        help_text="True = Каскадный расчет (сначала скидка продавца, потом промокод на остаток)."
    )
    is_active = models.BooleanField("Активное правило", default=True)

    class Meta:
        verbose_name = "Правило защиты скидок"
        verbose_name_plural = "Правила защиты скидок"


class AppliedOrderDiscount(TimestampedModel):
    """
    Детальная фиксация всех примененных скидок в заказе.
    """

    class DiscountSource(models.TextChoices):
        SELLER = "seller", "Скидка продавца"
        PLATFORM_PROMO = "platform_promo", "Промокод платформы"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="applied_discounts")
    order_item = models.ForeignKey(OrderItem, null=True, blank=True, on_delete=models.CASCADE,
                                   related_name="applied_discounts")

    source_type = models.CharField("Источник скидки", max_length=20, choices=DiscountSource.choices)
    seller_discount = models.ForeignKey(SellerDiscount, null=True, blank=True, on_delete=models.SET_NULL)
    promo_code = models.ForeignKey(PlatformPromoCode, null=True, blank=True, on_delete=models.SET_NULL)

    discount_amount = models.DecimalField("Примененная сумма скидки (UZS)", max_digits=14, decimal_places=2)
    note = models.CharField("Примечание / Лог расчета", max_length=255, blank=True)

    class Meta:
        verbose_name = "Примененная скидка в заказе"
        verbose_name_plural = "Примененные скидки в заказах"