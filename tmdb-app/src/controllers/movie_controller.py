from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime as dt
from src import db
from src.models.movie import Movie
from src.models.user import User
from src.errors import error_response


def update_existing_movie_rating(existing_movie, rating_user, genre=None):
    should_update_genre = bool(genre and not existing_movie.genre)

    if rating_user is None and not should_update_genre:
        return error_response(
            400,
            "Movie already exists. Provide rating_user to update it"
        )

    if rating_user is not None:
        existing_movie.rating_user = rating_user

    if should_update_genre:
        existing_movie.genre = genre

    db.session.commit()

    return jsonify({
        'message': 'Movie already exists. Data updated successfully',
        'movie': existing_movie.to_dict()
    }), 200


def _normalize_text(value):
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned if cleaned else None


def _find_existing_movie(title, synopsis):
    normalized_title = _normalize_text(title)
    normalized_synopsis = _normalize_text(synopsis)

    synopsis_filter = db.func.coalesce(
        db.func.lower(db.func.trim(Movie.synopsis)),
        ''
    )
    normalized_synopsis_value = (normalized_synopsis or '').lower()

    return Movie.query.filter(
        db.func.lower(db.func.trim(Movie.title)) == normalized_title.lower(),
        synopsis_filter == normalized_synopsis_value
    ).first()


def create_movie():
    if not request.is_json:
        return error_response(400, "Request must be JSON")
    
    data = request.get_json()
    title = data.get('title')
    release_date = data.get('release_date')
    synopsis = data.get('synopsis')
    rating = data.get('rating')
    img_url = data.get('imgUrl')
    roster = data.get('roster')
    genre = data.get('genre')
    user_id = data.get('user_id')
    rating_user = data.get('rating_user')

    title = _normalize_text(title)
    synopsis = _normalize_text(synopsis)
    genre = _normalize_text(genre)

    if not title:
        return error_response(400, "Title is required")
    
    try:
        parsed_date = None
        if release_date:
            try:
                parsed_date = dt.strptime(release_date, '%Y-%m-%d').date()
            except ValueError:
                return error_response(400, "Invalid date format. Use YYYY-MM-DD")
        
        if rating_user is not None:
            if not (0 <= rating_user <= 5):
                return error_response(400, "Rating must be between 0 and 5")
        
        if rating is not None:
            if not (0 <= rating <= 10):
                return error_response(400, "Rating must be between 0 and 10")

        if user_id is not None:
            user = User.query.get(user_id)
            if not user:
                return error_response(404, "User not found")

        existing_movie = _find_existing_movie(title=title, synopsis=synopsis)

        if existing_movie:
            return update_existing_movie_rating(existing_movie, rating_user, genre)
        
        new_movie = Movie(
            title=title,
            release_date=parsed_date,
            synopsis=synopsis,
            genre=genre,
            rating=rating,
            imgUrl=img_url,
            roster=roster,
            user_id=user_id,
            rating_user=rating_user
        )
        
        db.session.add(new_movie)
        db.session.commit()
        
        return jsonify({
            'message': 'Movie created successfully',
            'movie': new_movie.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, f"Error creating movie: {str(e)}")


def get_movies_rated():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '', type=str)
        year = request.args.get('year', type=int)
        genre = _normalize_text(request.args.get('genre', '', type=str))
        min_rating = request.args.get('min_rating', type=float)
        
        per_page = min(per_page, 100)
        
        query = Movie.query
        
        if search:
            query = query.filter(Movie.title.ilike(f'%{search}%'))

        if year is not None:
            if year < 1800 or year > 2100:
                return error_response(400, "Invalid year. Use a value between 1800 and 2100")
            query = query.filter(db.extract('year', Movie.release_date) == year)

        if genre:
            query = query.filter(
                db.func.lower(db.func.coalesce(Movie.genre, '')).like(f"%{genre.lower()}%")
            )
        
        if min_rating is not None:
            query = query.filter(Movie.rating >= min_rating)
        
        query = query.order_by(Movie.release_date.desc().nullslast())
        
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        movies = [movie.to_dict() for movie in pagination.items]
        
        return jsonify({
            'movies': movies,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        return error_response(500, f"Error fetching movies: {str(e)}")


def get_movie(movie_id):
    try:
        movie = Movie.query.get(movie_id)
        
        if not movie:
            return error_response(404, "Movie not found")
        
        return jsonify({
            'movie': movie.to_dict()
        }), 200
        
    except Exception as e:
        return error_response(500, f"Error fetching movie: {str(e)}")



@jwt_required()
def delete_movie(movie_id):
    try:
        current_user_id = get_jwt_identity()
        
        movie = Movie.query.get(movie_id)
        
        if not movie:
            return error_response(404, "Movie not found")
        
        if movie.user_id != current_user_id:
            return error_response(403, "You can only delete your own movies")
        
        title = movie.title
        
        db.session.delete(movie)
        db.session.commit()
        
        return jsonify({
            'message': f'Movie "{title}" deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, f"Error deleting movie: {str(e)}")


@jwt_required()
def re_rate_movie(movie_id):
    if not request.is_json:
        return error_response(400, "Request must be JSON")
    
    try:
        movie = Movie.query.get(movie_id)
        
        if not movie:
            return error_response(404, "Movie not found")
        
        data = request.get_json()
        rating = data.get('rating')
        
        if rating is None:
            return error_response(400, "Rating is required")
        
        if not isinstance(rating, (int, float)) or not (0 <= rating <= 5):
            return error_response(400, "Rating must be between 0 and 5")
        
        movie.rating = rating
        db.session.commit()
        
        return jsonify({
            'message': f'Movie "{movie.title}" rated successfully',
            'movie': movie.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, f"Error rating movie: {str(e)}")