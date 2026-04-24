# Deployment на Yandex Cloud VDS

Этот проект деплоится через GitHub Actions в два этапа:

1. `test` job работает на GitHub-hosted runner (`ubuntu-latest`).
2. `deploy` job работает на self-hosted runner внутри VDS `213.165.196.208`.

`deploy` запускается только на `push` в `main` после успешных тестов.

## 1. Подготовка GitHub

В репозитории создайте environment `production` и добавьте secrets:

- `X_API_KEY` — обязательный production API key длиной не меньше 32 символов.
- `LOG_LEVEL` — опционально, если не задан, workflow подставит `INFO`.
- `DEBUG_MODE` — опционально, если не задан, workflow подставит `false`.

Self-hosted runner должен быть зарегистрирован с labels:

- `yandex-vds`
- `production`

Итоговый job выбирает runner по набору labels:

```text
self-hosted, linux, x64, yandex-vds, production
```

## 2. Подготовка VDS

Ниже предполагается Ubuntu 22.04/24.04 и доступ по SSH.

Обновите пакеты и установите базовые зависимости:

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg ufw
```

Установите Docker Engine и Compose plugin по официальной схеме Docker для Ubuntu:

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
docker --version
docker compose version
```

Создайте отдельного пользователя для runner и дайте ему доступ к Docker:

```bash
sudo adduser --disabled-password --gecos "" actions
sudo usermod -aG docker actions
sudo mkdir -p /opt/actions-runner
sudo chown actions:actions /opt/actions-runner
```

## 3. Установка GitHub Actions runner

Переключитесь на пользователя `actions`:


sudo su - actions
cd /opt/actions-runner
```

Дальше откройте в GitHub:

`Repository -> Settings -> Actions -> Runners -> New self-hosted runner`

Выберите `Linux` и `x64`, затем выполните команды, которые покажет GitHub UI. При конфигурации runner добавьте labels:

```bash
./config.sh --url <repo-url> --token <token> --labels yandex-vds,production
```

После успешной регистрации установите runner как `systemd`-сервис. Важно: `svc.sh` нужно запускать именно из каталога runner. Команда вида `sudo /opt/actions-runner/svc.sh install` из домашней директории не подойдёт, потому что скрипт проверяет текущую рабочую директорию.

```bash
cd /opt/actions-runner
sudo ./svc.sh install actions
sudo ./svc.sh start
```

После этого убедитесь, что runner виден в GitHub как `Idle`.

## 4. Базовая защита хоста

Оставьте открытыми только SSH и HTTP-порт приложения:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 8000/tcp
sudo ufw enable
sudo ufw status
```

Runner лучше держать выделенным только под этот репозиторий и production deployment.

## 5. Что делает workflow при деплое

Workflow на self-hosted runner:

1. Чекаутит код репозитория.
2. Собирает `.env` из GitHub environment secrets.
3. Выполняет `docker compose -p zebrastat up -d --build --remove-orphans`.
4. Выполняет `docker compose -p zebrastat exec -T api python scripts/init_db.py`.
5. Проверяет `http://127.0.0.1:8000/health`.

Публичная проверка после деплоя:

```bash
curl http://213.165.196.208:8000/health
```

Ожидается ответ со `status: ok`.
