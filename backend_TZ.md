# СтройОптТорг — Backend TZ (jamoa uchun qabul qilingan ishchi variant)

**Versiya:** 2.0 — default qarorlar bilan, savollar bo'limisiz.  
**Status:** Dizayn asosidagi loyiha spetsifikatsiyasi; mentorning aniq taski va talablari har doim ustuvor.  
**Texnologiya:** Django + DRF + PostgreSQL; Python, pytest, drf-spectacular, django-filter.

## 1. Scope

Qurilish mollari e-commerce backend: foydalanuvchi, katalog, qidiruv/filtr, savatcha, sevimlilar/taqqoslash, chegirmalar, checkout, buyurtmalar, yetkazib berish, CMS va murojaatlar. Figma'dagi mobil/desktop variantlar bitta backend API'dan foydalanadi. To'lov provayderi, CDEK, SMS/email tashqi integratsiyasi **MVP'da yo'q**: ularning tanlovi va holati bazada qayd etiladi; real integratsiya alohida task.

## 2. Default biznes qoidalar (dizayn ko'rsatmagan joylarda jamoa taklifi)

1. **Valyuta:** RUB, `Decimal`, 2 kasr; maketda ₽ ko'rsatilgan. Narxlar backendda hisoblanadi.
2. **Guest:** katalog va qidiruv ochiq; savatcha session key orqali; guest checkout mumkin (checkout dizaynida login optional). User login qilganda guest cart merge qilish keyingi task.
3. **User:** email unique va login identifikatori; telefon alohida; password hash; email verification MVP'da majburiy emas. Parol reset tokenlari bir martalik va muddatli.
4. **Catalog:** Category daraxt; Product bir asosiy Category va Brand bilan bog'lanadi. SKU unique. Mahsulot variantlari alohida SKU modelisiz; o'lcham/rang kabi filtrlar Attribute/Option orqali. Keyin kerak bo'lsa ProductVariant qo'shiladi.
5. **Stock:** Product.stock_quantity >= 0; `is_active` bilan nashr qilish; buyurtma yaratilganda mavjudlik tekshiriladi. Zaxira (reservation) MVP'da yo'q.
6. **Cart:** bir savatchada bitta mahsulot bir marta; quantity > 0; server qayta narxlaydi.
7. **Discount:** mahsulot `sale_price` bo'lsa shuni oladi; promo va cart amount tier birga ishlatilishi mumkin, lekin chegirma manfiy totalga olib kelmaydi. Barcha chegirmalar serverda qayta hisoblanadi. Har buyurtmaga bitta promo.
8. **Orders:** statuslar `NEW`, `PROCESSING`, `COMPLETED`, `CANCELLED`; faqat staff o'zgartiradi. `OrderItem` nom, SKU, birlik narx va miqdorni snapshot qiladi. `Order` guest bo'lsa `user=NULL`; kontaktlar snapshot. Order yaratish `transaction.atomic`.
9. **Delivery:** `PICKUP`, `STORE_DELIVERY`, `CDEK_COURIER`, `CDEK_PVZ`; shahar, manzil va pickup point turi bo'yicha validatsiya; tashqi narx hisoblash integratsiyasiz admin'da sozlangan delivery fee.
10. **Payment:** `ONLINE_CARD`, `CASH_ON_PICKUP`, `OTP_CREDIT`, `SBER_CREDIT` kabi usul kodi; real to'lov o'tkazish MVP scope'da emas. `PaymentAttempt` kelajakdagi integratsiya uchun model, status `PENDING/PAID/FAILED/CANCELLED`; uni ishlatish alohida task.
11. **CMS:** Article, FAQ, Review, StaticPage, Banner, Promotion admin orqali boshqariladi. Review moderatsiyadan keyin ko'rinadi.
12. **Security:** customer faqat o'z profil/manzil/buyurtmasini ko'radi; staff admin'da boshqaradi; rate limiting, env secrets, logging, tests.

## 3. Modullar va funksiyalar

### Users
- Register: full_name, email, phone, region, password + confirm + privacy consent (confirm saqlanmaydi).
- Login, logout, password reset/change, profile edit, address CRUD.
- User va Address jadvallari; admin uchun `is_staff`, `is_superuser`.

### Catalog
- Category tree, Brand, Product, ProductImage, Attribute, AttributeOption, ProductAttributeValue.
- List/detail, qidiruv (name, SKU, brand), price range, brand/category, material/color/size va boshqa atribut filtrlari, sort va pagination.
- Mahsulot sahifasida asosiy rasm, galereya, tavsif, xususiyatlar, stock, o'xshash mahsulotlar.

### Shopping
- Cart, CartItem: guest session yoki user FK; item quantity; server-side totals.
- Favorite va ComparisonItem: userga bog'langan; guest compare keyingi iteratsiya.
- One-click buy request: `CallbackRequest`da `product` FK bilan qayd etiladi.

### Promotions
- Promotion: aksiya sahifasi uchun nom, tavsif, rasm, vaqt oralig'i.
- PromoCode: unique code, foiz yoki fixed, min order, limit, aktiv davr.
- CartDiscountTier: subtotal threshold va foiz; promo bilan qo'llash ketma-ketligi: product sale → cart tier → promo.

### Checkout / Orders
- Guest va customer order; delivery method, city, pickup point (tegishli usulda), address snapshot, payment method code.
- OrderItem narx snapshot; order totals: subtotal, tier_discount, promo_discount, delivery_fee, grand_total.
- Order list/detail faqat egasi uchun; guest order identifikatorini mijozga tasodifiy token orqali ko'rsatish alohida xavfsiz mexanizm bilan.
- Status update staff-only; order submit idempotency key orqali duplicate'dan himoyalanishi mumkin.

### Content / Leads
- Article list/detail, FAQ, Review, StaticPage, Banner; kontakt formasi, callback, newsletter.
- Privacy va cookie roziligi UI; backend faqat zarur rozilik vaqtini saqlaydi.

## 4. Asosiy ma'lumotlar arxitekturasi

`schema.dbml` — **field/type/relationship/unique bo'yicha yagona ERD manba**. Ushbu hujjatda jadval maydonlarini takrorlamaymiz; bir xil ma'lumotning ikki nusxasi farqlanib ketmasin.

## 5. API kontrakti (boshlang'ich)

- `/api/v1/auth/register/`, `/api/v1/auth/login/`, `/api/v1/auth/password-reset/`, `/api/v1/me/`, `/api/v1/me/addresses/`
- `/api/v1/categories/`, `/api/v1/brands/`, `/api/v1/products/`, `/api/v1/products/{slug}/`
- `/api/v1/cart/`, `/api/v1/cart/items/`, `/api/v1/cart/promo/`
- `/api/v1/favorites/`, `/api/v1/comparison/`
- `/api/v1/delivery/methods/`, `/api/v1/delivery/cities/`, `/api/v1/delivery/pickup-points/`
- `/api/v1/orders/`, `/api/v1/orders/{id}/`
- `/api/v1/articles/`, `/api/v1/promotions/`, `/api/v1/faq/`, `/api/v1/reviews/`, `/api/v1/pages/{slug}/`, `/api/v1/banners/`
- `/api/v1/callback-requests/`, `/api/v1/newsletter/`

## 6. Acceptance criteria

- Email va SKU unique; password hashed; duplicate registration rad etiladi.
- User boshqa user'ning address/order'iga kira olmaydi.
- Catalog category/brand/attribute/price filtrlari, sort va pagination ishlaydi.
- Cart quantity > 0, unique cart+product; narx clientdan olinmaydi.
- Promo expired/invalid/over limit rad etiladi; total >= 0.
- Checkout delivery va payment tanlovi valid; `OrderItem` snapshot katalog o'zgarishidan mustaqil.
- Django `check`, migrations, pytest, admin va OpenAPI ishlaydi.

## 7. Dizayn manbalari

`Регистрация`, `Авторизация`, `Личный кабинет`, `Каталог товаров`, `Карточка товара`, `Корзина`, `Оформление заказа`, `Сравнение`, `Избранные товары`, `Блог`, `Акции`, `Отзывы`, `Вопрос-ответ`, `Заказать звонок` va boshqa eksport qilingan ekranlar.

**Muhim:** bu hujjatdagi default qarorlar mentorning tasdiqlangan biznes talablari emas. Support aniq task berganda shu task scope'iga moslashtiriladi. Model kodini yozishdan avval `schema.dbml`ni mentor bilan kelishish kerak.
