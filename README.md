![Workflow](https://github.com/magicbuka/foodgram-project-react/actions/workflows/foodgram-workflow.yml/badge.svg)

# Foodgram

### Описание проекта Foodgram:

«Продуктовый помощник». На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Технологии:

Python 3.7  
Django 2.2  
Django Rest Framework  
Djoser  
Reportlab  
NGINX  
Gunicorn  
Docker  


### Как запустить проект:

Клонировать репозиторий:

```
git clone https://github.com/magicbuka/foodgram-project-react.git
```

Пример наполнения .env-файла:

```
SECRET_KEY=(ключ находится в настройках settings.py)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

Выполните команду для запуска проекта:

```
docker-compose up -d --build
```

Выполните по очереди команды для выполнения миграций, создания суперпользователя и подгрузки статики:

```
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic --no-input 
```

Заполнить базу данных тестовыми данными 

```
docker-compose exec web python manage.py loaddata
```

### Разработчики проекта:
- [Baranova Anna](https://github.com/magicbuka)
