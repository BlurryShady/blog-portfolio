# Blurry Shady Blog

Public-facing blog that powers [blog.blurryshady.dev](https://blog.blurryshady.dev) a Django 5.2 site with a neo-brutalist theme and curated publishing workflow. Visitors can browse categories, read posts and sign up to comment. Authors get draft previews, profile management and safe password-reset emails.

## Key Features
- **Modern publishing flow** – custom `PostQuerySet`, `published_at` timestamping, and draft previews so unfinished work stays private.
- **Authentication enhancements** – custom registration form (email required) and a fully branded password-reset experience.
- **Profiles & comments** – editable bios, avatars, locations and a spam-resistant comment form with themed controls.
- **SEO & discovery** – canonical tags, Open Graph/Twitter cards on every template, sitemap + robots and discoverable RSS/Atom feeds.
- **Visual identity** – animated eclipse background, neo-brutalist buttons, dark/light theme toggle and consistent CTA styling.

## Tech Stack
- **Backend:** Django 5.2, SQLite (dev) / PostgreSQL (recommended for prod)
- **Frontend:** Django templates, custom CSS/JS, responsive meta viewport
- **Utilities:** `django-cleanup`, Django sitemaps + feeds, console/SMTP email backends

## Project Structure
```
personalblog/
├─ blog/                # App: models, views, forms, templates
├─ personalblog/        # Core settings, URLs, WSGI
├─ static/              # CSS, JS, media placeholders
├─ templates/           # Project-level auth + password-reset templates
├─ media/               # Uploaded avatars/posts (dev)
├─ manage.py
└─ README.md
```

## Getting Started
1. **Clone & enter the project**
   ```bash
   git clone https://github.com/your-user/blurryshady-blog.git
   cd personalblog
   ```
2. **Create a virtual environment (Python 3.11+)**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # PowerShell on Windows
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   > If `requirements.txt` is missing, run `pip freeze > requirements.txt` once you finish installing Django, django-cleanup, etc., then commit the file.
4. **Create a `.env` (or use host-level env vars)** – see table below.
5. **Run migrations & seed data**
   ```bash
   py manage.py migrate
   py manage.py createsuperuser
   ```
6. **Start the dev server**
   ```bash
   py manage.py runserver
   ```

## Environment Variables
| Name | Required | Notes |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | ✅ | Generate a long random string in production. The repo default is dev-only. |
| `DEBUG` | optional | Set to `False` in production. |
| `ALLOWED_HOSTS` | ✅ | Comma-separated hostnames (e.g. `blog.blurryshady.dev,localhost`). |
| `EMAIL_HOST`, `EMAIL_PORT` | ✅ for prod | SMTP server from your domain provider (e.g. Mailgun, Brevo). Default port `587`. |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | ✅ for prod | SMTP login. Use app passwords if available. |
| `EMAIL_USE_TLS` / `EMAIL_USE_SSL` | optional | Defaults: TLS on, SSL off. Toggle per provider. |
| `DEFAULT_FROM_EMAIL` | optional | Defaults to `Blurry Shady Blog <noreply@blog.blurryshady.dev>`. |
| `DATABASE_URL` | optional | Configure when switching from SQLite to Postgres/MySQL (use `dj-database-url`). |

The settings file reads these variables at runtime. When `EMAIL_HOST` (and friends) are present, Django switches from the console backend to SMTP automatically, so password-reset emails go out through your domain.

## Running Tests
```bash
py manage.py test blog
```
Covers publishing visibility logic, preview gating, and regression tests for the manager/queryset.

## Static & Media Files
- In development, static files are served directly from `static/`; uploaded avatars land in `media/`.
- Before deploying, run `py manage.py collectstatic` and configure your platform to serve `STATIC_ROOT` (or use a CDN).
- Media uploads in production should be backed by S3, Azure Blob or Render Disk to avoid data loss during deploys.

## Deployment Checklist
1. `DEBUG=False`, `ALLOWED_HOSTS=['blog.blurryshady.dev']`, add `CSRF_TRUSTED_ORIGINS` for your HTTPS origin.
2. Provide unique `DJANGO_SECRET_KEY` and configure a production database if needed.
3. Set the SMTP env vars described above; verify SPF/DKIM records on your domain so reset emails aren’t flagged.
4. Run `py manage.py migrate && py manage.py collectstatic` on the server.
5. Configure process manager (Gunicorn/Uvicorn) + reverse proxy (nginx, Render, Fly.io, etc.).
6. Submit `https://blog.blurryshady.dev/sitemap.xml` to Google Search Console once live.

## Author
Crafted by **Blurry Shady**. Check out my main site: blurryshady.dev. Reach out via discord or any social media for freelancing or collaboration. I use **Blurry Shady** everywhere.
