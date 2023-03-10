# Yatube - социальная сеть для блогеров

Проект предназначен для публикации постов с картинками. Авторы публикаций могут подписываться на других авторов и оставлять комментарии к их публикациям.

## Используемые фреймворки и библиотеки:
- Python 3.7
- Django 2.2.16
- SQLite3
- HTML
- CSS

## Функционал

- Регистрация и восстановление доступа по электронной почте;
- Личная страница пользователя;
- Создание и редактирование собственных постов с изображением;
- Группировка постов в группы по интересам;
- Просмотр страниц других авторов;
- Возможность подписки и отписки от авторов;
- Отдельная лента с постами авторов на которых подписан пользователь;
- Комментирование постов других авторов;
- Модерация записей через панель администратора, управление пользователями и создание групп.
## Установка

Клонировать репозиторий:

   ```python
   git clone https://github.com/JUSTUCKER/Yatube_social_network.git
   ```

Перейти в папку с проектом:

   ```python
   cd yatube_social_network/
   ```

Создать виртуальное окружение (требуется версия Python >= 3.7):

   ```python
   python -m venv venv
   ```

Активировать виртуальное окружение::

   ```python
   # для OS Lunix и MacOS
   source venv/bin/activate
   ```

   ```python 
   # для OS Windows
   source venv/Scripts/activate
   ```

Установить зависимости из файла requirements.txt:

   ```python
   python3 -m pip install --upgrade pip
   ```

   ```python
   pip install -r requirements.txt
   ```

Выполнить миграции на уровне проекта:

   ```python
   cd yatube/
   ```
   ```python
   python3 manage.py migrate
   ```

Зарегистирировать суперпользователя:

   ```python
   python3 manage.py createsuperuser

   # адрес панели администратора
   http://127.0.0.1:8000/admin
   ```

Запустить проект:

   ```python
   python3 manage.py runserver

   # адрес запущенного проекта
   http://127.0.0.1:8000
   ```

## Авторы

- [@JUSTUCKER](https://github.com/JUSTUCKER) and [@yandex-praktikum](https://github.com/yandex-praktikum)
