# Avito Merch Store API

Автор: Тигран Согомонян

## Описание проекта

Это API для внутреннего магазина мерча в Avito. Сотрудники могут покупать товары (мерч) за монетки и передавать монетки друг другу. При первой аутентификации пользователь создается автоматически с начальным балансом 1000 монет.

## Функциональные возможности

- **Аутентификация:**  
  Эндпоинт `/api/auth` принимает имя пользователя и пароль. Если пользователь не найден, создается новый с балансом 1000 монет. В ответ возвращается JWT-токен для дальнейшей авторизации.

- **Получение информации:**  
  Эндпоинт `/api/info` предоставляет информацию о текущем балансе монет, инвентаре (списке купленных товаров) и истории переводов монет (отправленные и полученные).

- **Передача монет:**  
  Эндпоинт `/api/sendCoin` позволяет пользователю отправить монеты другому пользователю, если на его счете достаточно средств для перевода.

- **Покупка мерча:**  
  Эндпоинт `/api/buy/{item}` позволяет купить товар за монеты, списывая соответствующую сумму с баланса пользователя.

- **Список мерча:**  
  Эндпоинт `/api/merch` возвращает список всех доступных товаров для покупки в магазине.

## Стек технологий

- **Язык программирования:** Python 3.10  
- **Фреймворк:** FastAPI  
- **ORM:** SQLAlchemy  
- **База данных:** PostgreSQL (запускается через Docker)  
- **Аутентификация:** JWT (используется библиотека python-jose)  
- **Контейнеризация:** Docker, Docker Compose  
- **Тестирование:** pytest, pytest-cov

## Установка и запуск

1. **Клонируйте репозиторий:**

   ```bash
   git clone https://github.com/TigranSo/avito_merch_store.git
   cd avito_merch_store


Создайте файл .env в корне проекта, если его нет (я оставил пример, в нем не содержатся важные данные):

Содержимое файла:

DATABASE_URL=postgresql://admin:123@db/merch_store

SECRET_KEY=your_secret

Запустите Docker Compose для создания и запуска контейнеров:

docker-compose up --build

Контейнеры будут запущены:

db: PostgreSQL, доступен на порту 5432.

api: доступен на http://localhost:8080.

Проверьте работу API: Откройте http://localhost:8080/docs – это Swagger UI, где можно протестировать доступные эндпоинты.

Тестирование

ВАЖНО!

Для теста нужно будет открыть файл alembic.ini  и там строку закомментировать  sqlalchemy.url = postgresql://admin:123@db/merch_store 

и  раскомментировать  # sqlalchemy.url = sqlite:///./test.db (Чтобы использовать sqlite базу для теста)

Создайте виртуальное окружение:

python -m venv venv
Активируйте виртуальное окружение:

На Windows:

venv\Scripts\activate

На macOS/Linux:
source venv/bin/activate

Установите зависимости:

pip install -r requirements.txt

Запустите тесты с использованием pytest:

pytest --maxfail=1 --disable-warnings -q --cov=backend

Тесты покрывают более 80% кода проекта.

Проблемы и решения

При запуске API таблицы создавались автоматически в событии startup в файле backend/app/main.py:


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    # Инициализация мерча (если таблица пустая)
    ...
    
Это решение позволило избежать проблем с отсутствующими таблицами в базе данных.

В переменной окружения DATABASE_URL использовалось значение postgresql://admin:123@db/merch_store. Были проверены файлы .env и alembic.ini (если они используются) на корректную кодировку UTF-8, чтобы избежать ошибок Unicode.

Заключение

В репозитории содержатся:

Код сервиса – все файлы проекта находятся в ветке main.
Docker Compose – файл docker-compose.yml готов к запуску. Инструкция по запуску описана выше.
