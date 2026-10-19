# Productivity Notes API

A secure Flask REST API for storing and managing user-owned notes with JWT authentication.

## Features

- User signup and login with hashed passwords
- JWT-protected note endpoints
- User isolation so each account only sees its own notes
- Paginated notes listing
- Database migrations and seed data support

## Installation

1. Clone the project.
2. Install dependencies: `pipenv install`
3. Activate the virtual environment: `pipenv shell`
4. Initialize the database:

```bash
export FLASK_APP=app.py
flask db init
flask db migrate -m "initial migration"
flask db upgrade
```

5. Seed example data: `python seed.py`

The seed creates two users, `alice` and `bob`, both with the password `password123`.

## Run

```bash
export FLASK_APP=app.py
flask run
```

## Testing

```bash
pytest -v
```

## Endpoints

- `POST /signup` - create a user account
- `POST /login` - authenticate a user and return a JWT token
- `GET /me` - return the authenticated user's details
- `GET /notes?page=<int>&per_page=<int>` - list paginated notes for the current user
- `POST /notes` - create a new note for the current user
- `GET /notes/<id>` - fetch one note if it belongs to the current user
- `PATCH /notes/<id>` - update one note if it belongs to the current user
- `DELETE /notes/<id>` - delete one note if it belongs to the current user

## Auth Header

Include the JWT in the Authorization header: `Authorization: Bearer <token>`
