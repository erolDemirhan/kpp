# Piyasa Takip — Expo/FastAPI MVP

Yaklaşık 20 yetkili kullanıcı için USD/TRY, EUR/TRY, BIST 30/100, Borsa İstanbul payları ve TEFAS yatırım fonlarını izleyen Türkçe mobil MVP. Emir/alım-satım yoktur. Varsayılan veri **DEMO — sentetik veri** olup yatırım kararı için kullanılamaz.

## Mimari ve kararlar

- `apps/mobile`: Expo 54, Expo Router, React Native Paper, TanStack Query, strict TypeScript; açık/koyu sistem teması.
- `backend`: FastAPI + Pydantic + SQLAlchemy/Alembic. API ve sürekli çalışan tek worker aynı kodu kullanır, ayrı süreçlerdir. PostgreSQL kalıcı durum, alarm kilidi ve benzersiz olay anahtarı sağlar.
- Mobil veri sağlayıcıya gitmez. Provider sözleşmesi tek ortak çekim sağlar; gerçek mod bozulursa demoya düşmez.
- Tahmin: son fiyat baseline'ı ile son 20 log getirinin ortalaması (trend) ve standart sapması (oynaklık). 1 gün = sonraki işlem/değerleme günü, 1 hafta = sonraki 5 gün. P10/P50/P90 dağılım senaryolarıdır, “%80 kesinlik” değildir. En az 30 gözlem gerekir. MVP takvimi hafta sonlarını atlar; üretimde lisanslı Türkiye tatil/erken kapanış takvimi gerekir.
- Alarm eşikleri `Decimal`: yüzde düşüş `referans × (1-yüzde/100)`; eşitlik tetikler. Referans değer/kaynak/zaman sabittir. Tek seferlik olay `(alarm_id, quote_id)` ile idempotenttir.

## Sıfırdan yerel kurulum

Gerekenler: Docker/Compose, Node 20+, npm, Python 3.12 ve Expo development build destekli cihaz/emülatör.

```bash
cp backend/.env.example backend/.env
# Docker dışından çalıştıracaksanız DATABASE_URL hostunu localhost yapın
docker compose up --build
curl http://localhost:8000/health
cd apps/mobile && npm ci
cp .env.example .env
npx expo start --dev-client
```

Fiziksel telefonda `EXPO_PUBLIC_API_BASE_URL`, bilgisayarın telefonla aynı ağdaki IP'si olmalıdır (`http://192.168.x.x:8000`); güvenlik duvarında portu yalnız yerel ağa açın. `localhost` telefonun kendisidir.

Docker olmadan backend:

```bash
cd backend && python -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'
python -m app.seed
uvicorn app.main:app --reload
# ayrı terminal ve aynı ortam:
python -m app.worker
```

## Kimlik doğrulama ve yetki

Yerelde `APP_ENV=development`, `DEMO_AUTH=true` Firebase Emulator yerine deterministik demo kullanıcısını sağlar. Firebase Auth Emulator kullanılacaksa istemcide `EXPO_PUBLIC_USE_AUTH_EMULATOR=true`, backend'de emulator host ve proje kimliği ayarlanır; production'da `DEMO_AUTH=false` zorunludur. Production API, Firebase Admin Application Default Credentials ile ID token doğrular; ardından yönetici UID'yi ekler:

```sql
INSERT INTO allowed_users(uid,email,active) VALUES ('firebase-uid','kullanici@example.com',true);
```

Admin JSON yalnız sunucu secret mount'unda tutulur; Git'e veya `EXPO_PUBLIC_*` içine konmaz. Firebase web istemci config'i gizli değildir fakat ayrı tutulur.

## Bildirim ve build

`expo-notifications` izni sonrasında Expo push token API'ye kaydedilir; çıkış akışı `/devices/{token}` ile pasiflemelidir. Worker kalıcı olay üretir, kontrollü retry durumu saklar. Ticket kabulü cihaz teslimi değildir; üretimde receipt polling ile `DeviceNotRegistered` token pasifleştirme kalan iştir.

Android uzak push **Expo Go ile test edilmez**. Firebase projesinde FCM V1 service account'u EAS'e yükleyin; iOS için Apple Developer üyeliği, bundle ID ve APNs anahtarı/provisioning gerekir. Kimlik bilgisi olmadan gerçek push veya imzalı build tamamlanmış sayılmaz.

```bash
cd apps/mobile
npx eas build --profile development --platform android
npx eas build --profile preview --platform android   # dahili APK
npx eas build --profile development --platform ios   # Apple imzalama gerekir
```

## Ortam değişkenleri

| Değişken | Taraf | Gizli | Örnek/açıklama |
|---|---|---:|---|
| `EXPO_PUBLIC_API_BASE_URL` | mobil | hayır | `http://192.168.1.50:8000` |
| `EXPO_PUBLIC_FIREBASE_*` | mobil | hayır | Firebase istemci config'i |
| `EXPO_PUBLIC_USE_AUTH_EMULATOR` | mobil | hayır | yalnız yerelde `true` |
| `DATABASE_URL` | sunucu | evet | PostgreSQL bağlantısı |
| `GOOGLE_APPLICATION_CREDENTIALS` | sunucu | evet | Firebase Admin secret dosya yolu |
| `DATA_PROVIDER` | sunucu | hayır | `demo`; gerçek ad erişim kurulmadan çalışmaz |
| `OPENAI_API_KEY` | sunucu | evet | boşsa doğrulanabilir şablon açıklama |
| `OPENAI_MODEL` | sunucu | hayır | model deployment adı |
| `WORKER_INTERVAL_SECONDS` | worker | hayır | sağlayıcı kota/yayın sıklığına göre |
| `DAILY_LLM_LIMIT` | sunucu | hayır | günlük maliyet üst sınırı |

OpenAI anahtarı yokken fiyat, alarm ve sayısal tahmin çalışır; mevcut MVP teknik kanıttan şablon açıklama döndürür. Structured Outputs adaptörünün anahtarla doğrulanması tamamlanmadan LLM entegrasyonu tamamlanmış sayılmaz.

## Üretim ve maliyet

Deploy, sürekli çalışan **üç ayrı bileşen** ister: HTTP API, worker ve PostgreSQL. Scheduler yalnız HTTP sürecinde değildir. Piyasa verisi lisans/yeniden dağıtım bedeli, API/veritabanı/worker altyapısı ve opsiyonel LLM token maliyeti ayrı izlenmelidir; sabit ya da ücretsiz oldukları varsayılmaz. Kaynak ve hak incelemesi: [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md).

## Testler ve sınırlar

```bash
cd backend && pytest && ruff check .
cd apps/mobile && npm run lint && npm run typecheck
```

Testler sentetik sağlayıcıyı kullanır; gerçek BIST/TEFAS, gerçek Firebase ve push entegrasyon testi değildir. MVP'nin bilinen üretim işleri `docs/TASKS.md` içindedir. OpenAPI: `http://localhost:8000/docs`.
