# Постоянное размещение на VPS

Этот набор запускает PostgreSQL, FastAPI и Caddy. В интернет открыты только
HTTPS-порты `80` и `443`; PostgreSQL, API и загруженные файлы остаются внутри
Docker-сети и постоянных Docker-томов.

## Перед запуском

1. Возьмите VPS с Ubuntu 22.04/24.04 и публичным IPv4.
2. Купите или используйте домен и создайте DNS-запись `A`: например,
   `api.example.com` -> публичный IP VPS.
3. Откройте в панели VPS или firewall только TCP-порты `22`, `80` и `443`.
4. Установите Docker Engine и Docker Compose plugin по официальной инструкции
   Docker для вашей версии Ubuntu.

## Запуск

```bash
git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ> maintenance-api
cd maintenance-api
cp .env.production.example .env
nano .env
docker compose -f docker-compose.production.yml up -d --build
docker compose -f docker-compose.production.yml ps
```

В `.env` обязательно укажите настоящий `DOMAIN`, новый `SECRET_KEY` и сложный
`POSTGRES_PASSWORD`. После того как DNS обновится, Caddy автоматически получит
и продлит TLS-сертификат. Проверка: `https://<DOMAIN>/health`.

## Сборка мобильного приложения

После проверки API соберите APK с публичным HTTPS-адресом:

```bash
flutter build apk --release --dart-define=API_URL=https://<DOMAIN>/api/v1
```

Такой APK будет работать из любой сети. При смене домена или пути API его нужно
пересобрать с новым `API_URL`.

## Обновление

```bash
git pull
docker compose -f docker-compose.production.yml up -d --build
```

Не публикуйте `.env`, PostgreSQL-порт `5432`, pgAdmin и секреты в интернете.
