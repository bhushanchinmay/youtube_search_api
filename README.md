# Backend Assignment

API to fetch latest videos sorted in reverse chronological order of their publishing date-time from YouTube for a given tag/search query in a paginated response.

## Tech-Stack

* Python (Backend Language)
* Django (Python Framework)
* Django REST framework (REST API Toolkit)
* SQLite (Database)

## Instructions

*  Clone this repo <br>
*  Create and activate Python Virtual Environment <a href="https://docs.python.org/3/library/venv.html"> (reference) </a>
*  Install dependencies
 > pip install -r requirements.txt
*  Go to **youtube_api** folder
> cd youtube_api
*  Set up the **database**
> python manage.py migrate
*  Create superuser to access the dashboard
> python manage.py createsuperuser
*  Start the server
> python manage.py runserver
*  Access the dashboard through the address generated
> http://127.0.0.1:8000/admin
