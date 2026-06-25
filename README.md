# Microservicio 2FA

Genera un código de doble factor tras el login, lo envía por **Gmail (SMTP XOAUTH2)**
y lo **valida** para que tu API principal confíe en el resultado. Hecho en **FastAPI**
con **arquitectura hexagonal**.

## Arquitectura

Dos features, cada una con `domain` (puertos + entidades), `application` (casos de
uso) e `infraestructure` (adaptadores, controllers, routers, dependencies):

- **`two_factor`** → genera el código y lo **envía** por Gmail.
  - Adaptadores: `gmail_token_provider` (refresh_token → access_token) y
    `gmail_api_email_sender` (API REST de Gmail + plantilla `html/correo.html`).
  - Transporte por defecto: **API de Gmail** (scope `gmail.send`). Existe también
    `smtp_email_sender` (SMTP XOAUTH2) si regeneras el token con scope
    `https://mail.google.com/`; para usarlo, cámbialo en `dependencies.py`.
- **`oauth`** → relaciona el código con el usuario y lo **valida**.
  - Dueña de la persistencia (`sql_code_repository`) y del caso de uso `verify`.

> La carpeta original `2FA` se renombró a `two_factor` porque en Python un paquete
> no puede empezar por un dígito (`import ...2FA` es inválido).

## Flujo

```
API principal --(POST /2fa/send {email})-->  microservicio
                                              · genera código
                                              · lo guarda (oauth)  ──> BD
                                              · lo envía por Gmail ──> correo del usuario

usuario introduce el código en tu app
API principal --(POST /2fa/verify {email,code})--> microservicio
                                              <-- {"valid": true/false, "reason": ...}
```

## Endpoints

| Método | Ruta          | Body                        | Respuesta                                  |
|--------|---------------|-----------------------------|--------------------------------------------|
| POST   | `/2fa/send`   | `{"email": "..."}`          | `{"email","sent":true,"expires_at"}`       |
| POST   | `/2fa/verify` | `{"email":"...","code":"..."}` | `{"email","valid":bool,"reason"}`       |
| GET    | `/health`     | —                           | `{"status":"ok"}`                          |

`reason` en verify: `ok`, `no_active_code`, `expired`, `invalid_code`.
El código es de un solo uso: al validarse correctamente se consume.

## Ejecutar

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
# Docs interactivas: http://localhost:8001/docs
```

## Configuración (`.env`)

Las credenciales de Gmail OAuth2 ya están. Otras variables relevantes:

- `DATABASE_URL` → por defecto SQLite local. Para Postgres:
  `postgresql+asyncpg://user:pass@host:5432/db` (instala `asyncpg`).
- `CODE_LENGTH` (6) y `CODE_TTL_SECONDS` (300, caducidad del código).
- `SMTP_HOST` / `SMTP_PORT` → `smtp.gmail.com:587`.

## Integración con tu API principal

```python
import httpx
BASE = "https://tu-servicio.up.railway.app"  # URL pública de Railway

# tras validar usuario/contraseña (cualquier email del usuario sirve):
httpx.post(f"{BASE}/2fa/send", json={"email": user_email})

# cuando el usuario envía el código:
r = httpx.post(f"{BASE}/2fa/verify", json={"email": user_email, "code": code})
if r.json()["valid"]:
    ...  # emitir sesión / token
```

## Docker

```bash
docker build -t microservicio-2fa .
docker run -p 8001:8001 --env-file .env microservicio-2fa
```

El contenedor escucha en `$PORT` (cae a `8001` si no está definido).

## Desplegar en Railway

1. Sube el repo a GitHub y en Railway: **New Project → Deploy from GitHub repo**.
   Railway detecta el `Dockerfile` y el `railway.json` (healthcheck en `/health`).
2. **Variables** (Settings → Variables): el `.env` **no** se sube (está en
   `.gitignore`/`.dockerignore`), así que define ahí cada variable:

   ```
   GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN,
   GMAIL_FROM, GMAIL_FROM_NAME
   CODE_LENGTH=6, CODE_TTL_SECONDS=300
   ```

   `PORT` lo inyecta Railway automáticamente (no lo definas tú).
3. **Base de datos**: añade el plugin **PostgreSQL** (New → Database → PostgreSQL).
   Railway crea la variable `DATABASE_URL`; el microservicio la convierte solo a
   `postgresql+asyncpg://...`. Sin Postgres usaría SQLite, que en Railway se
   **borra en cada redeploy** (no recomendado).
4. Railway expone una URL pública (`https://...up.railway.app`) — esa es la `BASE`
   que usa tu API principal.
