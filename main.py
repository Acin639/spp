from flask import Flask, request, jsonify

from vhx import gethome, search
from category import get_category
from gallery_profile import get_gallery, get_profile


app = Flask(__name__)


# ============================================================
# HOME API
# Example: /api/home?limit=10
# ============================================================

@app.route("/api/home", methods=["GET"])
def home_api():
    try:
        limit = request.args.get("limit", default=10, type=int)

        if limit < 1:
            return jsonify({
                "success": False,
                "error": "limit must be greater than 0"
            }), 400

        videos = gethome(limit)

        return jsonify({
            "success": True,
            "count": len(videos),
            "videos": videos
        })

    except Exception:
        app.logger.exception("Home API error")

        return jsonify({
            "success": False,
            "error": "Unable to get homepage videos"
        }), 500


# ============================================================
# SEARCH API
# Example: /api/search?q=hello&page=1&pages=3&limit=20
# ============================================================

@app.route("/api/search", methods=["GET"])
def search_api():
    try:
        keyword = request.args.get("q", "").strip()

        if not keyword:
            return jsonify({
                "success": False,
                "error": "Search query is required. Use ?q=your-search"
            }), 400

        page = request.args.get("page", default=1, type=int)

        if page < 1:
            return jsonify({
                "success": False,
                "error": "page must be greater than 0"
            }), 400

        pages_value = request.args.get(
            "pages", default="1"
        ).strip()

        if pages_value.lower() == "all":
            pages = None
        else:
            try:
                pages = int(pages_value)
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": "pages must be a number or 'all'"
                }), 400

            if pages < 1:
                return jsonify({
                    "success": False,
                    "error": "pages must be greater than 0"
                }), 400

        limit_value = request.args.get(
            "limit", default="10"
        ).strip()

        if limit_value.lower() == "all":
            limit = None
        else:
            try:
                limit = int(limit_value)
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": "limit must be a number or 'all'"
                }), 400

            if limit < 1:
                return jsonify({
                    "success": False,
                    "error": "limit must be greater than 0"
                }), 400

        videos = search(
            keyword,
            page=page,
            pages=pages,
            limit=limit
        )

        return jsonify({
            "success": True,
            "query": keyword,
            "page": page,
            "pages": "all" if pages is None else pages,
            "limit": "all" if limit is None else limit,
            "count": len(videos),
            "videos": videos
        })

    except Exception:
        app.logger.exception("Search API error")

        return jsonify({
            "success": False,
            "error": "Unable to perform search"
        }), 500


# ============================================================
# CATEGORY API
# Example: /api/category/amateur
# ============================================================

@app.route("/api/category/<string:category>", methods=["GET"])
def category_api(category):
    try:
        category = category.strip()

        if not category:
            return jsonify({
                "success": False,
                "error": "Category is required"
            }), 400

        results = get_category(category)

        return jsonify({
            "success": True,
            "category": category,
            "count": len(results),
            "results": results
        })

    except Exception:
        app.logger.exception("Category API error")

        return jsonify({
            "success": False,
            "error": "Unable to get category results"
        }), 500


# ============================================================
# GALLERY API
# Example: /api/gallery
# Calls get_gallery() without arguments.
# ============================================================

@app.route("/api/gallery", methods=["GET"])
def gallery_api():
    try:
        gallery = get_gallery()

        return jsonify({
            "success": True,
            "gallery": gallery
        })

    except Exception:
        app.logger.exception("Gallery API error")

        return jsonify({
            "success": False,
            "error": "Unable to get gallery"
        }), 500


# ============================================================
# PROFILE API
# Example: /api/profile
# Calls get_profile() without arguments.
# ============================================================

@app.route("/api/profile", methods=["GET"])
def profile_api():
    try:
        profile = get_profile()

        return jsonify({
            "success": True,
            "profile": profile
        })

    except Exception:
        app.logger.exception("Profile API error")

        return jsonify({
            "success": False,
            "error": "Unable to get profile"
        }), 500


# ============================================================
# API INFORMATION
# ============================================================

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "name": "VHX Video API",
        "status": "online",
        "endpoints": {
            "home": "/api/home?limit=10",
            "search": "/api/search?q=hello&page=1&pages=3&limit=20",
            "category": "/api/category/amateur",
            "gallery": "/api/gallery",
            "profile": "/api/profile",
            "health": "/api/health"
        }
    })


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "success": True,
        "status": "online"
    })


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False,
        threaded=True
    )