
# Google Trends Proxy

Basit bir Flask tabanlı Google Trends proxy'si.

## Endpointler

- `GET /` – sağlık kontrolü
- `GET /trends?geo=US` – günlük trend aramalar
- `GET /trends?q=bitcoin&geo=US` – belirli keyword için explore endpoint

## Render'da Deploy

1. Bu repo'yu GitHub'a yükle.
2. Render > New Web Service > Public Git repo URL'sini gir.
3. Ortaya çıkan URL'yi n8n'de kullan:  
   `https://senin-servis-adın.onrender.com/trends?geo=US`
