# API şeması

Çalışan OpenAPI `/openapi.json`, Swagger `/docs` adresindedir. `/instruments` arama; `/{id}/quote|history|forecast` piyasa/tahmin; `/watchlist`, `/alarms`, `/notifications`, `/devices` kullanıcı kaynaklarıdır. `userId` istemciden alınmaz; doğrulanmış Firebase UID ve `allowed_users` kaydı kullanılır.
