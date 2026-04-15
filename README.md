# Air Quality Prediction (EnviroAir)

Flask app for MySQL signup/login, CSV upload/preview, and ML-based air quality prediction. **UI uses Tailwind CSS via CDN** (no project CSS files). Gallery/hero images use remote Unsplash/Pixabay URLs.

## Folder structure

```
project/
├── app.py                 # Flask application (run this)
├── requirements.txt
├── README.md
├── run_app.bat            # Windows: create venv, install deps, run app
├── templates/             # Jinja2 HTML pages
│   ├── nav.html           # Shared navbar (logged-in users)
│   ├── home.html
│   ├── login.html
│   ├── signup.html
│   ├── upload.html
│   ├── prediction.html
│   ├── preview.html
│   ├── gallery.html
│   ├── performance.html
│   └── chart.html
├── static/
│   └── js/
│       └── script.js      # Preview page: scroll-to-bottom helper
├── models/                # Optional: put airs.pkl here (preferred)
├── airs.pkl               # Or keep the trained model here (fallback)
└── airQuality.csv         # Sample data (if present)
```

## How to run (order matters)

Open **PowerShell** or **Command Prompt**, go to the project folder, then run **in this order**:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Then open: `http://127.0.0.1:5000` (you will be redirected to `/login` until you sign in).

**Notes**

- Always **activate `.venv`** before `pip install` and `python app.py`, or use `.\.venv\Scripts\python.exe` directly so `flask` is found.
- **Windows shortcut:** double‑click `run_app.bat` (same steps, automated).

## Tech stack

- **Backend:** Python 3.11, Flask, sessions
- **DB:** MySQL + `flask-mysqldb` (optional if package missing; auth will show an error)
- **ML:** scikit-learn, numpy, scipy, pandas, pickle (`airs.pkl`)
- **Frontend:** HTML + **Tailwind CDN** + Google Charts (chart page) + Font Awesome (performance page)

## Authentication

- Public: `/login`, `/signup`, `POST /log`, `POST /insertvalues`
- Protected: home, upload, prediction, preview, gallery, performance, chart, `POST /predict`, `POST /getdata`
- Logout: `GET /logout`

## MySQL setup

Create database `air_quality` and table `signup` with columns `username`, `email`, `password` (see earlier project SQL if needed).

## Model file

Place **`airs.pkl`** in **`models/airs.pkl`** (preferred) or in the **project root** next to `app.py`. The app tries `models/` first, then root.

## Security (demo)

Passwords are stored in plain text in MySQL. For production, hash passwords and use HTTPS.
