# LINE Login Demo — FastAPI JWT Authentication

English | [繁體中文](README.zh-TW.md)

A backend demo built with **FastAPI** that implements third-party login (LINE Login) and JWT authentication end to end: the OAuth2 authorization flow, user persistence, JWT issuance, and protected-route verification.

## Background

This project is extracted from a personal expense-splitting app (AABro) I am developing. It isolates the **Auth module** to showcase a complete third-party login and authorization implementation, without any expense-splitting business logic.

## Tech Stack

| Category | Technology |
|---|---|
| Web framework | FastAPI |
| Database | PostgreSQL 15 |
| ORM | SQLAlchemy 2.0 |
| Authentication | LINE Login (OAuth2) + JWT (PyJWT) |
| Containerization | Docker, Docker Compose |
| Session management | Starlette SessionMiddleware (for CSRF `state` validation) |
| Testing | Pytest |

## Features

- **LINE OAuth2 login flow**: generates and validates the `state` parameter to prevent CSRF attacks.
- **User upsert**: on first login, creates the user and the third-party account binding; on subsequent logins, looks up the existing account.
- **JWT issuance and verification**: issues a JWT with an expiry after successful login, with explicit handling for expired and malformed tokens.
- **Protected route example (`/api/auth/me`)**: shows how to protect endpoints using FastAPI dependency injection (`Depends`).
- **Test coverage of auth logic**: Pytest cases cover all four branches of the authentication dependency.

## Project Structure

```
app/
├── api/
│   ├── auth.py          # LINE login and callback routes
│   └── deps.py          # Auth dependency (get_current_user)
├── models/
│   └── db/
│       └── user.py      # User / UserOAuthBinding table definitions
├── services/
│   └── auth_service.py  # Core logic: OAuth token exchange, JWT encode/decode
├── db.py
└── main.py
postgres/
└── init.sql             # Database initialization script
tests/                   # Pytest test suite
```

**Layered design**: `api/` handles HTTP requests and framework integration (routes, dependencies), while `services/` holds framework-independent business logic that can be tested in isolation.

## Prerequisites

- Docker / Docker Compose
- A LINE Developers account with a LINE Login channel (Channel ID / Channel Secret)

## Getting Started

1. Copy the environment template and fill in real values:

```bash
cp .env.example .env
```

Edit `.env` and set `LINE_CHANNEL_ID`, `LINE_CHANNEL_SECRET`, `JWT_SECRET`, and other variables.

2. Build and start the containers:

```bash
docker compose up --build
```

3. Open `http://localhost:8000/docs` for the interactive API docs.

## API Endpoints

| Method | Path | Description | Auth required |
|---|---|---|---|
| GET | `/api/health` | Service health check | No |
| GET | `/api/db-check` | Database connectivity check | No |
| GET | `/api/auth/line` | Redirects to the LINE authorization page | No |
| GET | `/api/auth/line/redirect` | LINE callback; issues a JWT | No |
| GET | `/api/auth/me` | Returns the current user's profile | **Yes (Bearer token)** |

## Testing

**Option 1: Swagger UI**
1. Complete the LINE login flow and copy the JWT from the redirect URL.
2. On `/docs`, click **Authorize** and paste the JWT.
3. Call `/api/auth/me` and confirm the user data is returned.

**Option 2: Command line**

```bash
curl -H "Authorization: Bearer <your JWT>" http://localhost:8000/api/auth/me
```

**Option 3: Automated tests**

```bash
pytest
```

**Covered scenarios**:
- Valid token → `200` with user data
- Missing token → `401`
- Invalid or tampered token → `401`
- Expired token → `401` with a re-login prompt

## Known Limitations and Future Improvements

This is a demo project. The following simplifications are intentional and known:

- **LINE `id_token` signature is not verified**: the payload is only decoded (`verify_signature=False`). In production, verify the signature using LINE's public JWKS keys.
- **JWT is passed to the frontend via URL query string**: after the callback, the token is appended to the redirect URL as a demo-stage shortcut. In production, use an `httpOnly` + `secure` cookie with a CSRF token to avoid exposing the token in browser history or server logs.
- **`JWT_SECRET` has a default value**: always override it in `.env` with a randomly generated, strong secret before deployment.

## License

MIT
