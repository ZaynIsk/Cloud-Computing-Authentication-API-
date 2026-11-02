# Week 4 Auth API

A small FastAPI authentication API built for the Advanced Cloud Computing module (MSc Data Analytics and AI, Birkbeck). Users can register, log in to receive an expiring JWT, and use that token to access a protected profile route.

**Tech:** Python, FastAPI, SQLAlchemy, SQLite, Pydantic, pwdlib (Argon2 password hashing), PyJWT, pytest.

**Python version:** 3.10 or later (developed on Python 3.14).

## Endpoints

| Method | Route | What it does |
|---|---|---|
| GET | `/` | Checks the API is running |
| POST | `/auth/register` | Creates a user. Returns `201` with `id`, `username` and `email` (never the password) |
| POST | `/auth/login` | Checks email and password. Returns a bearer token, or `401` for wrong credentials |
| GET | `/profile/me` | Protected. Returns the logged-in user, or `401` without a valid token |

Registration rules: `username` 3–50 characters, `email` must be a valid address, `password` at least 6 characters. A duplicate email returns `409`; invalid data returns `422`.

## Project structure

```text
week4-auth-api/
  main.py            # entry point used by Uvicorn
  application.py     # create_app(): builds the app and its tables
  database.py        # SQLite connection, sessions and get_db
  models.py          # User table (stores a password hash, not the password)
  schemas.py         # Pydantic request and response schemas
  security.py        # password hashing, JWT creation and get_current_user
  routers/
    auth.py          # /auth/register and /auth/login
    profile.py       # /profile/me
  tests/
    conftest.py      # test client with a temporary database
    test_auth.py     # unit and API tests
  requirements.txt
```

## Setup

Clone the repository and move into it:

```bash
git clone <repository-url>
cd week4-auth-api
```

Create and activate a virtual environment.

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

## Set the JWT signing secret

The app signs tokens with a secret read from the `JWT_SECRET` environment variable. It must be at least 32 characters, and the app will not start without it.

Generate one:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Set it in the terminal you will run the server from.

macOS/Linux:

```bash
export JWT_SECRET="<your-generated-secret>"
```

Windows PowerShell:

```powershell
$env:JWT_SECRET = "<your-generated-secret>"
```

Keep the value private. Never commit it, screenshot it or paste it into a file in this repository. Reuse the same value after restarting the terminal; changing it invalidates existing tokens.

## Run the app

```bash
uvicorn main:app --reload
```

Open the interactive docs at <http://127.0.0.1:8000/docs>, then:

1. **Register:** `POST /auth/register` with:
   ```json
   {
     "username": "student",
     "email": "student@example.com",
     "password": "secret123"
   }
   ```
2. **Log in:** `POST /auth/login` with the same email and password. Copy the `access_token` from the response.
3. **Authorise:** click **Authorize** at the top of the page, paste the token and confirm.
4. **Profile:** `GET /profile/me`. It returns your user. Without a token it returns `401`.

Tokens expire after 30 minutes; log in again to get a new one.

## Database

SQLite creates `auth.db` in the project folder the first time the app starts. It is excluded from Git by `.gitignore`, so each person who runs the project gets their own empty database.

The tests never use `auth.db`. Each test gets a fresh temporary SQLite database, and `tests/conftest.py` sets a test-only `JWT_SECRET`, so no real secret is needed to run them.

## Run the tests

From the project folder, with the environment active:

```bash
python -m pytest -q
```

**Result:** 6 passed.

| Test | Checks |
|---|---|
| `test_password_hash` | Hashing hides the password; the right password verifies and a wrong one does not |
| `test_login_and_profile` | Register (`201`, no password returned), log in, then reach `/profile/me` with the token |
| `test_profile_requires_token` | `/profile/me` without a token returns `401` |
| `test_login_with_wrong_password` | Wrong password returns `401` with `Invalid email or password` |
| `test_invalid_data` | Short username, bad email and short password return `422` |
| `test_duplicate_registration` | Registering the same email twice returns `409` with `Email already registered` |

A deprecation warning about `httpx` from FastAPI's test client may appear. It does not affect the results.

## Limitations

- SQLite suits local development only; a deployed version would use a managed database.
- There is no logout or token refresh; tokens simply expire after 30 minutes.
- No roles or permissions yet: any logged-in user can only read their own profile.
