import os
import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "1b35b5ccec8ac00f0812a458217dc13b").strip()
TMDB_BASE = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

GENRES = {
    28:"Action",12:"Adventure",16:"Animation",35:"Comedy",80:"Crime",
    99:"Documentary",18:"Drama",10751:"Family",14:"Fantasy",36:"History",
    27:"Horror",10402:"Music",9648:"Mystery",10749:"Romance",
    878:"Science Fiction",10770:"TV Movie",53:"Thriller",10752:"War",37:"Western"
}

def tmdb(path, params=None):
    if not TMDB_API_KEY:
        raise RuntimeError("TMDB_API_KEY is missing. Add your TMDB API key as an environment variable.")
    params = dict(params or {})
    params["api_key"] = TMDB_API_KEY
    response = requests.get(f"{TMDB_BASE}{path}", params=params, timeout=15)
    response.raise_for_status()
    return response.json()

def shape(movie):
    return {
        "id": movie.get("id"),
        "title": movie.get("title") or movie.get("original_title") or "Untitled",
        "original_title": movie.get("original_title", ""),
        "overview": movie.get("overview") or "No synopsis is available.",
        "release_date": movie.get("release_date") or "",
        "year": (movie.get("release_date") or "")[:4],
        "rating": movie.get("vote_average"),
        "vote_count": movie.get("vote_count", 0),
        "language": (movie.get("original_language") or "").upper(),
        "poster": f"{IMAGE_BASE}{movie['poster_path']}" if movie.get("poster_path") else "",
        "backdrop": f"https://image.tmdb.org/t/p/w1280{movie['backdrop_path']}" if movie.get("backdrop_path") else "",
        "genres": [GENRES.get(g, "Other") for g in movie.get("genre_ids", [])],
        "genre_ids": movie.get("genre_ids", [])
    }

def paged_results(data):
    return [shape(m) for m in data.get("results", [])]

@app.route("/")
def home():
    return render_template("index.html")

@app.get("/api/status")
def status():
    return jsonify({"configured": bool(TMDB_API_KEY), "provider": "TMDB"})

@app.get("/api/genres")
def genres():
    return jsonify([{"id":k,"name":v} for k,v in GENRES.items()])

@app.get("/api/discover")
def discover():
    try:
        page = max(1, min(request.args.get("page", 1, type=int), 500))
        genre = request.args.get("genre", "").strip()
        language = request.args.get("language", "").strip()
        sort = request.args.get("sort", "popularity.desc")
        allowed_sorts = {"popularity.desc","vote_average.desc","primary_release_date.desc","revenue.desc"}
        if sort not in allowed_sorts: sort = "popularity.desc"
        params = {"include_adult":"false","include_video":"false","sort_by":sort,
                  "page":page,"vote_count.gte":10}
        if genre and genre.isdigit(): params["with_genres"] = genre
        if language and language != "all": params["with_original_language"] = language
        data = tmdb("/discover/movie", params)
        return jsonify({"results":paged_results(data),"page":data.get("page",1),
                        "total_pages":data.get("total_pages",1),"total_results":data.get("total_results",0)})
    except RuntimeError as e: return jsonify({"error":str(e)}), 503
    except requests.RequestException: return jsonify({"error":"Could not reach TMDB. Check your connection and API key."}), 502

@app.get("/api/search")
def search():
    q = request.args.get("q","").strip()
    if not q: return jsonify({"results":[],"total_results":0})
    try:
        page = max(1, min(request.args.get("page",1,type=int),500))
        data = tmdb("/search/movie", {"query":q,"include_adult":"false","page":page})
        return jsonify({"results":paged_results(data),"page":data.get("page",1),
                        "total_pages":data.get("total_pages",1),"total_results":data.get("total_results",0)})
    except RuntimeError as e: return jsonify({"error":str(e)}), 503
    except requests.RequestException: return jsonify({"error":"Could not reach TMDB. Check your connection and API key."}), 502

@app.get("/api/movie/<int:movie_id>")
def movie_details(movie_id):
    try:
        data = tmdb(f"/movie/{movie_id}", {"append_to_response":"credits"})
        genres = [g["name"] for g in data.get("genres",[])]
        return jsonify({
            "id":data.get("id"),"title":data.get("title"),"overview":data.get("overview"),
            "year":(data.get("release_date") or "")[:4],"release_date":data.get("release_date"),
            "rating":data.get("vote_average"),"vote_count":data.get("vote_count"),
            "language":(data.get("original_language") or "").upper(),"genres":genres,
            "runtime":data.get("runtime"),"poster":f"{IMAGE_BASE}{data['poster_path']}" if data.get("poster_path") else "",
            "backdrop":f"https://image.tmdb.org/t/p/w1280{data['backdrop_path']}" if data.get("backdrop_path") else "",
            "tagline":data.get("tagline",""),
            "cast":[c.get("name") for c in data.get("credits",{}).get("cast",[])[:5]]
        })
    except RuntimeError as e: return jsonify({"error":str(e)}),503
    except requests.RequestException: return jsonify({"error":"Could not load movie details."}),502

@app.get("/api/recommend/<int:movie_id>")
def recommend(movie_id):
    try:
        params={"page":1}
        data=tmdb(f"/movie/{movie_id}/recommendations",params)
        results=paged_results(data)
        if len(results)<6:
            similar=tmdb(f"/movie/{movie_id}/similar",{"page":1})
            seen={m["id"] for m in results}
            results += [m for m in paged_results(similar) if m["id"] not in seen]
        return jsonify({"results":results[:12]})
    except RuntimeError as e: return jsonify({"error":str(e)}),503
    except requests.RequestException: return jsonify({"error":"Could not load recommendations."}),502

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
