import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv(
    'SECRET_KEY',
    default='dyjvlw%g@)ized$cn=r1n-k2^+%r!3-kqy)9*)#w$1yn-2-i!1'
)

DEBUG = os.getenv('DEBUG', True)

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', default=['*'])

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'django_filters',
    'users.apps.UsersConfig',
    'api.apps.ApiConfig',
    'recipes.apps.RecipesConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'foodgram.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'foodgram.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': os.getenv(
            'DB_ENGINE',
            default='django.db.backends.postgresql'
        ),
        'NAME': os.getenv('DB_NAME', default='postgres'),
        'USER': os.getenv('POSTGRES_USER', default='postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', default='postgres'),
        'HOST': os.getenv('DB_HOST', default='localhost'),
        'PORT': os.getenv('DB_PORT', default='5432')
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend', )

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 6,
}

DJOSER = {
    'SERIALIZERS': {
        'user_create': 'api.serializers.CustomUserCreateSerializer',
        'user': 'api.serializers.CustomUserSerializer',
        'current_user': 'api.serializers.CustomUserSerializer',
    },
    'PERMISSIONS': {
        'user': ('rest_framework.permissions.IsAuthenticated', ),
        'user_list': ('rest_framework.permissions.AllowAny', ),
    },
    'HIDE_USERS': False,
}

SLUG_ERROR = (
    'Можно использовать цифры и латинские буквы. Не более 200 символов'
)
WRONG_USERNAME = '"me" - недопустимое имя пользователя!'
WRONG_SYMBOLS = 'Недопустимые символы: {}'
WRONG_COOKING_TIME = 'Время приготовления должно быть больше 0!'
WRONG_UNIQUE_TAGS = 'Тэги должны быть уникальными!'
WRONG_UNIQUE_INGREDIENTS = 'Ингредиенты должны быть уникальными!'
WRONG_INGREDIENT_CHOOSE = 'Нужно выбрать хотя бы один ингредиент!'
WRONG_TAG_CHOOSE = 'Нужно выбрать хотя бы один тэг!'
WRONG_INGREDIENT_AMOUNT = 'Количество ингредиента должно быть больше нуля!'
USER_NOT_EXIST = 'Такого пользователя не существует.'
SUBSCRIBE_NOT_EXIST = 'Отсутствует подписка на данного пользователя.'
DELETE_FOLLOWING = 'Осуществлена отписка от пользователя {}.'
EMPTY_VALUE = '-пусто-'
