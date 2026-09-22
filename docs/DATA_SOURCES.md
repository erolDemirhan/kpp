# Veri kaynakları ve kullanım hakları

> MVP `demo-synthetic` modundadır. Değerler tekrarlanabilir sentetik veridir ve **DEMO — sentetik veri** etiketi taşır. Gerçek provider hatasında otomatik demo geçişi yoktur.

## Döviz — TCMB EVDS / gösterge kuru

- [EVDS web servis kılavuzu](https://evds2.tcmb.gov.tr/help/videos/EVDS_Web_Service_Usage_Guide.pdf) ve [TCMB kurları](https://www.tcmb.gov.tr/kurlar/kurlar_tr.html).
- Günlük gösterge kuru, işlem yapılabilir canlı kotasyon değildir. EVDS anahtarı gerekir; kota, yeniden dağıtım ve analiz hakkı üretimden önce TCMB ile yazılı doğrulanmalıdır. Alış/satış/orta ayrı `quoteType` olur.

## Borsa İstanbul — BISTECH / lisanslı dağıtıcı

- [Resmî veri ürünleri](https://www.borsaistanbul.com/tr/sayfa/171/veri-urunleri) ve [veri dağıtımı](https://www.borsaistanbul.com/tr/sayfa/172/veri-dagitim).
- XU030/XU100 ile pay son işlemleri için Borsa İstanbul veya yetkili dağıtıcı sözleşmesi gerekir. Gecikmeli/canlı gösterim, yeniden dağıtım, geçmiş ve türetilmiş analiz hakları sözleşmeye bağlıdır; 20 kullanıcı muafiyet değildir. Endpoint/kota uydurulmamıştır. Endeks `POINT`, pay para birimidir.

## Yatırım fonu — TEFAS

- [Resmî TEFAS](https://www.tefas.gov.tr/) ve [fon analiz ekranı](https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod=).
- Kapsam günlük yatırım fonu birim pay değeridir; borsa yatırım fonu son işlemi değildir. Değerleme tarihi ile yayın/alım zamanı ayrıdır. Üretim yeniden dağıtımına izin veren belgelenmiş API sözleşmesi doğrulanmadığından scraping yapılmadı. Takasbank/TEFAS ile erişim, kota, geçmiş, gösterim ve analiz hakları yazılı netleştirilmelidir.

## Kayıt ve durum

Her fiyat provider, instrumentId, `seriesId`, quoteType, currency/unit, asOf, receivedAt, delaySeconds ve durum taşır. `fresh`, `delayed`, `market_closed`, `outage`, `invalid` ayrıdır. Provider değişimi yeni seri kimliği oluşturur; sessiz birleştirme yoktur. Kurumsal işlem şüphesinde alarm durur, referans otomatik düzeltilmez.
