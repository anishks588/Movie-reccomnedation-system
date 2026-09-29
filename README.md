# CineMatch Worldwide — Full-stack movie discovery & recommendation app

CineMatch Worldwide is an IMDb-inspired learning project for exploring movies from many countries and languages. It uses **TMDB's movie database and API** for live search, discovery, ratings, posters, details and recommendations. It is not affiliated with IMDb and does not display IMDb ratings.

## Features
- Worldwide movie search by title
- Discover popular and top-rated movies
- Genre, original-language and sort filters
- Posters, synopsis, release year, vote average and vote count
- Movie details and cast
- Similar movie recommendations from TMDB
- Responsive frontend
- Python Flask backend and JSON API
- No local database required

## Get a TMDB API key
1. Create an account on The Movie Database (TMDB).
2. Request an API key from your account's API settings, following TMDB's current terms.
3. Set the key as an environment variable named `TMDB_API_KEY`. Do not publish your key or commit it to a public repository.

### Windows PowerShell
```powershell
$env:TMDB_API_KEY="YOUR_TMDB_API_KEY"
python app.py
```

### Windows CMD
```cmd
set TMDB_API_KEY=YOUR_TMDB_API_KEY
python app.py
```

### macOS / Linux
```bash
export TMDB_API_KEY="YOUR_TMDB_API_KEY"
python app.py
```

## Install and run
Python 3.9+ recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in a browser. Keep the terminal running while using the app.

## API routes
- `GET /api/status` — check whether a key is configured
- `GET /api/genres` — genre list
- `GET /api/discover?page=1&genre=28&language=hi&sort=popularity.desc`
- `GET /api/search?q=parasite&page=1`
- `GET /api/movie/496243` — movie details and cast
- `GET /api/recommend/496243` — related recommendations

## Technology
- Frontend: HTML5, CSS3, JavaScript (Fetch API)
- Backend: Python, Flask, Requests
- Data source: TMDB API
- Recommendation provider: TMDB recommendations and similar-title endpoints

## Important notes
- TMDB vote averages are not IMDb ratings. Ratings, availability and catalogue coverage may differ from IMDb.
- Search/discovery results depend on TMDB's live API and its current catalogue.
- The app requires internet access and a valid TMDB API key.
- This is an educational prototype. Review TMDB API terms, attribution requirements and rate limits before public deployment.
- Do not add your API key directly to `app.py`, frontend JavaScript, screenshots or a public repository.
