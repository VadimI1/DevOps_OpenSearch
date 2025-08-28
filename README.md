# OpenSearch
Простое веб-приложение для поиска документов в OpenSearch с использованием FastAPI.
## Требования
- Docker
- Docker Compose
- Python 3.9+ (для локальной разработки)
## Установка и запуск
1. Настройка переменных окружения
    
Создайте файл .env в корне проекта:
```env
OPENSEARCH_HOST='http://localhost:9200'
OPENSEARCH_USERNAME=admin
OPENSEARCH_PASSWORD=adminpassword
```

2. Запуск приложения
```bash
# Сборка и запуск контейнеров
docker-compose up --build

# Запуск в фоновом режиме
docker-compose up -d --build
```
## API Endpoints
### Основные endpoints:
```GET /``` - Информация о приложении

```POST /init``` - Инициализация индекса и загрузка тестовых данных

```GET /search``` - Поиск документов
## Структура проекта
```
DevOps_OpenSearch/
├── docker-compose.yml      # Docker Compose конфигурация
├── Dockerfile              # Docker образ приложения
├── requirements.txt        # Python зависимости
├── app.py                 # Основное приложение
├── .env                   # Переменные окружения
├── .dockerignore          # Игнорируемые файлы для Docker
└── README.md              # Документация
```
##  Конфигурация
### Параметры OpenSearch
Настраиваются через переменные окружения в файле .env:

|Переменная|Описание|Значение по умолчанию|
|-|--------|---|
|```OPENSEARCH_HOST```|URL OpenSearch|```http://localhost:9200```|
|```OPENSEARCH_USERNAME```|Имя пользователя|```admin```|
|```OPENSEARCH_PASSWORD```|Пароль|```adminpassword```|

### Параметры поиска
- ```q``` (обязательный) - поисковый запрос

- ```content_type``` (опциональный) - фильтр по типу контента: 
```article```, ```news```, ```tutorial```, ```review```
