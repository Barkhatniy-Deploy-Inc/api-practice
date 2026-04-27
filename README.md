# Зебра-стат API

FastAPI backend для анализа данных о дорожно-транспортных происшествиях. Приложение использует SQLite через async SQLAlchemy и запускается через `uvicorn app.main:app`.

## Docker Compose

Создайте локальный файл окружения:

```bash
cp .env.example .env
```

Замените `X_API_KEY` и `AUTH_SALT` в `.env` на собственные секреты, затем запустите сервис:

```bash
docker compose up --build
```

Поднимается сервис `api` на порту `8000`. SQLite-файл хранится в volume `sqlite_data`, логи приложения — в volume `app_logs`.

## CI/CD и production deployment

Тесты продолжают выполняться на GitHub-hosted runner (`ubuntu-latest`), а production-деплой вынесен на self-hosted runner в Yandex Cloud VDS `213.165.196.208`.

- `pull_request` в `main` или `master`: запускается только `test` job.
- `push` в `main`: после успешных тестов запускается `deploy` job на self-hosted runner с labels `self-hosted`, `linux`, `x64`, `yandex-vds`, `production`.
- Деплой использует `docker compose -p zebrastat up -d --build --remove-orphans`, затем выполняет `python -m scripts.init_db` и `python -m scripts.seed_db` внутри контейнера, проверяет наполнение справочников и подтверждает доступность `http://127.0.0.1:8000/health`.

Для GitHub нужно создать environment `production` и заполнить secrets:

- `X_API_KEY` — обязателен.
- `AUTH_SALT` — обязателен. Это стабильная секретная соль для хеширования выданных API-ключей.
- `LOG_LEVEL` — опционален, по умолчанию `INFO`.
- `DEBUG_MODE` — опционален, по умолчанию `false`.

Пошаговая инструкция по подготовке VDS и регистрации self-hosted runner описана в [docs/deployment_yandex_cloud.md](/home/xytrax/projects/api-practice/docs/deployment_yandex_cloud.md).

## VDS

Production VDS в Yandex Cloud: `213.165.196.208`.

После запуска Docker Compose на сервере API будет доступен на:

```bash
http://213.165.196.208:8000
```

Healthcheck на сервере:

```bash
curl http://213.165.196.208:8000/health
```

## Инициализация базы данных

В проекте нет Alembic-миграций. Таблицы создаются скриптом:

```bash
docker compose run --rm api python -m scripts.init_db
```

Справочники регионов и округов загружаются отдельным шагом:

```bash
docker compose run --rm api python -m scripts.seed_db
```

Для локального запуска без Docker используйте тот же скрипт после установки зависимостей:

```bash
python -m scripts.init_db
python -m scripts.seed_db
```

## Healthcheck

Проверка доступности приложения:

```bash
curl http://localhost:8000/health
```

Ожидаемый ответ содержит `status: ok` и версию приложения.

## Тесты

Локальный запуск тестов:

```bash
X_API_KEY=test_key_for_ci_checks_only_must_be_long_enough AUTH_SALT=test_auth_salt_for_ci_checks_only_123456 pytest -q
```

Линтер в проекте пока не настроен. Его можно добавить позже отдельным решением, когда будет выбран стандарт форматирования и статического анализа.

## Переменные окружения

Обязательные:

- `X_API_KEY` — мастер-ключ длиной минимум 32 символа.
- `AUTH_SALT` — стабильная секретная соль длиной минимум 16 символов. Если изменить её позже, уже выданные API-ключи перестанут совпадать с хешами в БД.

Опциональные:

- `DATABASE_URL` — строка подключения к БД. В Docker Compose используется `sqlite+aiosqlite:////app/data/dtp.db`.
- `LOG_LEVEL` — уровень логирования, по умолчанию `INFO`.
- `DEBUG_MODE` — режим отладки, по умолчанию `false`.

## Локальный запуск без Docker

```bash
python -m pip install -r requirements.txt
X_API_KEY=test_key_for_local_run_at_least_32_chars AUTH_SALT=test_auth_salt_for_local_run_123456 uvicorn app.main:app --host 0.0.0.0 --port 8000
```
