# Project Name: Cars Dealership — Full-Stack Capstone

**Repository name:** `Cars-Dealership-Full-Stack-Capstone-assignment`  
**Project name:** `Cars Dealership Full-Stack Application`

## Project overview

A responsive dealership directory for browsing US dealer branches, viewing customer reviews, registering and signing in, posting reviews, and analyzing review sentiment. This repository contains the Django application, React signup component, demo data, CI workflow, API evidence, and deployment configuration.

## Technology stack

- **Backend:** Python, Django, SQLite
- **Frontend:** React, Vite, JavaScript, CSS
- **Authentication:** Django session authentication
- **Testing and automation:** Django tests, GitHub Actions
- **Deployment starter:** Docker and Render Blueprint

## Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/DakshDhaundiyal/Cars-Dealership-Full-Stack-Capstone-assignment)

Alternatively, open the [Render Blueprint setup page](https://dashboard.render.com/blueprint/new?repo=https://github.com/DakshDhaundiyal/Cars-Dealership-Full-Stack-Capstone-assignment), review the checked-in `render.yaml`, and choose **Deploy Blueprint**. Once Render finishes provisioning, copy the actual public service URL into the rubric's `deploymentURL` file and use the deployed-evidence workflow to capture screenshots from that live service.

## Run locally

From the repository root:

```bash
pip install -r requirements.txt
cd server
python manage.py migrate
```

To create a local demo login only for coursework screenshots:

**Linux/macOS/Git Bash**
```bash
CREATE_DEMO_USER=true DEMO_USER_PASSWORD='ChooseYourLocalTestPassword123!' python manage.py seed_data
```

**Windows PowerShell**
```powershell
$env:CREATE_DEMO_USER="true"
$env:DEMO_USER_PASSWORD="ChooseYourLocalTestPassword123!"
python manage.py seed_data
```

Then start the server:

```bash
python3 manage.py runserver
```

Open `http://127.0.0.1:8000/`; the Django admin is available at `/admin/`. Demo-account creation is disabled by default and requires both `CREATE_DEMO_USER=true` and `DEMO_USER_PASSWORD`. Never enable a shared demo account in production.

Run the React development frontend separately:

```bash
cd server/frontend
npm install
npm run dev
```

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/fetchDealers` | All dealers with location and display-name fields |
| GET | `/fetchDealers/Kansas` | Dealers in Kansas |
| GET | `/fetchDealer/1` | Details for one dealer |
| GET | `/fetchReviews/dealer/1` | Reviews with purchase and vehicle details |
| GET | `/djangoapp/get_cars` | Car makes grouped with their models |
| GET | `/djangoapp/api/dealers/` | Current API listing; accepts `?state=Kansas` |
| GET | `/djangoapp/api/dealers/<id>/` | Current API dealer details |
| GET | `/djangoapp/api/dealers/<id>/reviews/` | Current API reviews for a dealer |
| POST | `/djangoapp/api/register/` | Create a user account |
| POST | `/djangoapp/api/login/` | Start a session |
| POST | `/djangoapp/api/logout/` | End a session |
| POST | `/djangoapp/api/reviews/` | Post a review while logged in |
| GET | `/djangoapp/api/car-makes/` | Flat list of available makes and models |
| POST | `/djangoapp/api/analyze-review/` | Analyze review sentiment |

## Rubric files

- [About Us page](server/frontend/static/About.html)
- [Contact Us page](server/frontend/static/Contact.html)
- [React Sign-up component](server/frontend/src/components/Register/Register.jsx)
- [Evidence checklist](docs/EVIDENCE_CHECKLIST.md)
- [cURL examples](docs/curl-examples.md)
- [GitHub Actions workflow](.github/workflows/ci.yml)

The terminal output, browser screenshots, CI/CD logs, and deployment URL included with the capstone should be generated from a running app and an actual successful workflow. The workflow in this repository regenerates the local API output files and screenshot evidence on successful runs. Live deployment screenshots can only be produced after a real deployment URL is available.

## Security and deployment notes

Set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, and `DJANGO_ALLOWED_HOSTS` for production. Use HTTPS, secure session cookies, and a production database. Sample dealer records, staff contact details, and `.example` email addresses are illustrative data. Sentiment analysis is a lightweight lexicon-based demo, not a clinical or financial classifier.
