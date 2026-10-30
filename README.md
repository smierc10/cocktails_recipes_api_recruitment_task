# Cocktails api backend recrutment task
Django &amp; DRF backend built as a recruitment task for SOLVRO in a form of cocktail recipe platform, featuring custom filtering, media handling, and OpenAPI docs.

## Requirments
- python (tested on 3.14.8)
- django
- djangorestframework
- django-filter
- drf-spectacular
- drf-nested-routers

## Core features
- **REST architecture** built using DRF viewsets, routers (normal and nested)
- **custom filtering and ordering** using django-filters
- **API Documentation** generated OpenAPI schema with interactive swagger ui
- **Authentication user** login system which supports staff status which allows content moderation
- basic image upload endpoint which allows posting images to server and making them publicly available via provided url
- a few test cases that check if basic functionality is working

## Tech Stack

- **Language:** Python
- **Framework:** Django, Django REST Framework
- **Filtering:** `django-filter`
- **Documentation:** `drf-spectacular`
- **Database:** SQLite (local development)

## Installation and running
### 1. Clone/download the repository and navigate into the project folder
```
git clone github.com/smierc10/cocktails_recipes_api_recruitment_task
cd cocktails_recipes
```

### 2. Set up the database
```
python manage.py makemigrations
python manage.py migrate
```

### 3. Load initial data (if provided)
```
python manage.py loaddata initial_data.json
```

### 4. Create an admin superuser
```
python manage.py createsuperuser
```

### 5. Start the development server
```
python manage.py runserver
```

## Knows Issues
- user handle (unique string identifying the user) system is redundant as it takes on the role of username and id, in more complicated system it might have some benefits but in this case it was neither needed nor useful
- currently all image_url fields don't support relative urls which means the user needs to include an absolute url to the image even if its hosted on the same server
  - the system does not use it's built in image hosting capability (in which case it would use database relations) to support images from outside sources making it easier to import mock data

## AI Disclaimer
provided initial_data.json was generated using ai to allow easier testing 
