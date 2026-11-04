# СтройОптТорг — Backend jamoa roadmap

**Status:** Ishchi reja (mentor topshiriqlari ustuvor)  
**Repo:** https://github.com/RozimuhammadDev06/Mini-grup_21  
**Jamoa:** 4 developer, support mentor tasklarni taqsimlaydi va tekshiradi.  
**Asos:** Figma eksportidagi sahifalar; `backend_TZ.md` va `schema.dbml`.

## 0. Ish qoidalari

- Hozir remote'da faqat `main` bor. `main`ni `prod`ga o'zgartirmang, `staging`ni mentor roziligisiz yaratmang.
- Har developer o'z **feature branch**ida ishlaydi: `feature/<issue>-<mavzu>` (masalan `feature/12-catalog-models`), `main`dan yoki mentor belgilagan integration branch'dan olinadi.
- Branch'ni remote'ga `git push -u origin <branch>` bilan yuborish; **hech qachon `main`/`staging`ga to'g'ridan-to'g'ri push qilmaslik**. PR review va CI o'tgandan keyin vakolatli shaxs merge qiladi.
- Repo egasi ruxsatlarni belgilaydi. `main` himoyasi va required reviews admin tomonidan sozlanadi.
- Har bir task: GitHub Issue/mentor topshirig'i → branch → commit → push → PR → review → merge.
- **ERD tasdiqlanmaguncha Django models/migrations yozilmaydi.** Lokal setup va hujjat tayyorlash mumkin, lekin umumiy repo'ga faqat kelishilgan o'zgarishlar yuboriladi.
- Hech kim boshqa developerning branchini `force push` qilmaydi. `.env`, parollar, tokenlar, haqiqiy mijoz ma'lumotlari commit qilinmaydi.

## 1. Talablar va TZ (birinchi natija)

- [ ] Dizayn ekranlarini modulga ajratish: auth, catalog, shopping, checkout, content, contacts.
- [ ] `backend_TZ.md`ni jamoa bilan ko'rib chiqish.
- [ ] Qabul qilingan default biznes qoidalarni belgilash: guest checkout, currency RUB, promo kombinatsiyasi, order statuslari va h.k.
- [ ] Mentor task/scope'iga moslab talablarni qisqartirish yoki kengaytirish.
- **Done:** bir-biriga zid bo'lmagan talablar va modellarga traceability mavjud.

## 2. Database dizayn / ERD (modelsdan OLDIN)

- [ ] `schema.dbml`ni https://dbdiagram.io saytiga import qilish; jadval va FK chiziqlarini tekshirish.
- [ ] Har bir jadvalning field, type, nullability, default, unique va FK'larini tekshirish.
- [ ] User model va authentication identifikatori (`email`)ni aniqlash.
- [ ] Product attribute/filter modeli, price/stock, promo, order snapshot'ni muhokama qilish.
- [ ] ERD screenshot/PDF va `schema.dbml`ni mentor review'ga yuborish.
- **Done:** mentor ERDni ma'qullagan yoki aniq tuzatishlar ro'yxatini bergan.

## 3. Git va development environment

- [ ] Support bilan branch flow'ni kelishish: `feature/* → staging → main` yoki `feature/* → main`.
- [ ] PyCharm'da repo'ni ochish; Python venv yaratish.
- [ ] Django, DRF, PostgreSQL driver, pytest, drf-spectacular va django-filter uchun dependency management tanlash.
- [ ] `config` va `apps` strukturasi, `settings`/`.env.example`, `.gitignore`, README.
- [ ] PostgreSQL local yoki Docker Compose, Django check, database connection.
- [ ] CI: `python manage.py check`, lint, pytest (support bilan kelishilgan holda).
- **Done:** 4 developer README bo'yicha loyihani bir xil ishga tushira oladi.

## 4. Django models va migrations (ERD approval'dan KEYIN)

- [ ] `users`: Custom User (AUTH_USER_MODEL migratsiyadan oldin), Address.
- [ ] `catalog`: Category, Brand, Product, ProductImage, Attribute, AttributeOption, ProductAttributeValue.
- [ ] `shopping`: Cart, CartItem, Favorite, ComparisonItem.
- [ ] `promotions`: Promotion, PromoCode, CartDiscountTier.
- [ ] `delivery`: City, DeliveryMethod, PickupPoint.
- [ ] `orders`: Order, OrderItem, PaymentAttempt.
- [ ] `content`: Article, FAQ, Review, StaticPage, Banner, CallbackRequest, NewsletterSubscription.
- [ ] FK on_delete, unique constraints, indexes, Decimal va validation; `makemigrations`, `migrate`, `check`.
- [ ] DBeaver'da PostgreSQL ERD ochish; `schema.dbml` bilan solishtirish.
- **Done:** migrations clean, schema approved, sample objects yaratish mumkin.

## 5. Django Admin

- [ ] Har modul uchun admin: list_display, list_filter, search_fields, readonly_fields, inlines.
- [ ] Admin permissionlari va order tarixining snapshot fieldlarini readonly qilish.
- [ ] Admin orqali katalog, promo, buyurtma, maqola, bannerlarni boshqarish.
- **Done:** staff CRUD'ni admin'da xavfsiz bajaradi.

## 6. API va biznes logika

- [ ] Auth: register, login, logout/token refresh, password reset/change, profile, addresses.
- [ ] Catalog: categories, products, detail, search, filter, sort, pagination.
- [ ] Shopping: cart CRUD, favorites, compare, promo apply.
- [ ] Checkout: shipping options, pickup points, order create/detail/list, one-click request.
- [ ] Content: articles, promotions, FAQ, reviews, static pages, banners, callback, newsletter.
- [ ] Permissions, serializers, server-side totals, atomic order creation, validation, error responses.
- [ ] OpenAPI/Swagger.
- **Done:** endpointlar TZ'dagi acceptance criteria bo'yicha ishlaydi.

## 7. Testing, review va release

- [ ] pytest: models, constraints, auth, object permissions, catalog filters, cart totals, promo rules, checkout transaction, order snapshots.
- [ ] `select_related`/`prefetch_related`, query count, pagination, throttling.
- [ ] PR description: nima o'zgardi, qaysi Issue, migration bormi, test natijalari.
- [ ] CI green + review → staging; smoke test → mentor approval → main.
- **Done:** dokumentatsiya va testlar bilan qayta ishga tushiriladigan backend.

## 8. Mentor uchun topshirish paketi

1. `backend_TZ.md` — ishlash uchun qabul qilingan talablar.
2. `schema.dbml` — barcha jadval, field va relationship'lar.
3. `ERD_overview.png` / `ERD_overview.svg` — ko'rgazmali diagramma.
4. `roadmap.md` — ketma-ketlik va acceptance criteria.

## 9. Birinchi amaliy Git qadamlari (faqat lokal branch)

```bash
cd ~/Desktop/Mini-grup_21
git status
git switch main
git pull --ff-only origin main
git switch -c docs/backend-tz-erd
# roadmap.md, backend_TZ.md, schema.dbml, ERD_overview.* ni repo'ga nusxalang
git status
git add roadmap.md backend_TZ.md schema.dbml ERD_overview.png
git commit -m "docs: add backend roadmap, specification and ERD draft"
# Push qilishdan oldin mentor branch tartibini tasdiqlasin:
# git push -u origin docs/backend-tz-erd
```

**Eslatma:** ushbu branch hujjatlar uchun; models yozish uchun keyin alohida `feature/...` branch ochiladi. `main`ga merge faqat PR orqali.
