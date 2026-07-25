# EvTap — Əmlak Elanları Platforması (Demo)

Bu, Django ilə yazılmış, **tamamilə orijinal** bir əmlak elan platformasıdır. Bina.az kimi real
platformalardan yalnız ümumi UX konsepsiyaları (kateqoriya gəzintisi, axtarış/filtr, elan detalları,
elan yerləşdirmə) ilhamla hazırlanıb — bütün marka, dizayn, mətn və verilər orijinaldır və uydurmadır.

**Bu layihə real bina.az ilə heç bir əlaqəyə malik deyil.** Bütün istifadəçilər, elanlar, qiymətlər
kurgusaldır. Ödəniş axını tamamilə **DEMO/simulyasiyadır** — real bir ödəniş sistemi inteqrasiya
olunmayıb, heç bir kart məlumatı toplanmır.

## Quraşdırma

```powershell
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
copy .env.example .env   # SECRET_KEY-i dəyişin
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_data --count 40
python manage.py runserver
```

Sonra `http://127.0.0.1:8000/` ünvanına daxil olun.

## Demo hesablar

- Admin panel (`/admin/`): `seed_data` işlədilməzdən əvvəl `createsuperuser` ilə yaratdığınız hesab.
- Demo istifadəçilər (`seed_data` tərəfindən yaradılır): `demo_*` istifadəçi adları, parol: `demo12345`.

## Əsas axınlar

- Qeydiyyat → Elan yerləşdir → Admin təsdiqi → Elan önə çıxar (DEMO ödəniş) → Sevimlilərə əlavə et.
- Bütün elan/qiymət/istifadəçi verisi `core/management/commands/seed_data.py` tərəfindən uydurulur.

## Texniki qeydlər

- Stack: Django 6, django-filter, Pillow, django-environ, Bootstrap 5 (CDN) + orijinal `evtap.css`.
- App strukturu: `core`, `accounts`, `listings`, `promotions` (promosyon/DEMO ödəniş məntiqi qəsdən
  ayrı saxlanılıb ki, real ödəniş inteqrasiyasına keçid asan olsun).
- `promotions` app-ında heç bir real ödəniş provayderi yoxdur — hər şey `Promotion` modelində
  simulyasiya olunur.
