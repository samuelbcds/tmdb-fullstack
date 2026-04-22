import { api } from './api';
import { getPosterUrl, type Movie, type MovieDetails } from './tmdbService';

export interface BackendMovieDetails {
  id: number;
  title: string;
  synopsis?: string | null;
  genre?: string | null;
  release_date?: string | null;
  rating?: number | null;
  imgUrl?: string | null;
  rating_user?: number | null;
}

export interface MovieDetailsFromBackend extends MovieDetails {
  rating_user?: number | null;
}

interface GetMoviesResponse {
  movies: BackendMovieDetails[];
  pagination?: {
    page: number;
    pages: number;
    has_next: boolean;
  };
}

function mapBackendMovieToMovieDetails(movie: BackendMovieDetails): MovieDetailsFromBackend {
  const genreNames = (movie.genre || '')
    .split(',')
    .map((genre) => genre.trim())
    .filter(Boolean);

  return {
    id: movie.id,
    title: movie.title,
    original_title: movie.title,
    overview: movie.synopsis || '',
    poster_path: movie.imgUrl || null,
    backdrop_path: null,
    release_date: movie.release_date || '',
    vote_average: movie.rating ?? 0,
    vote_count: 0,
    popularity: 0,
    adult: false,
    genre_ids: [],
    original_language: 'pt-BR',
    video: false,
    genres: genreNames.map((name, index) => ({
      id: index + 1,
      name,
    })),
    runtime: 0,
    status: 'released',
    tagline: '',
    rating_user: movie.rating_user ?? null,
  };
}

export const getMovieDetailsFromBackend = async (movieId: number): Promise<MovieDetailsFromBackend> => {
  try {
    const response = await api.get(`/movies/${movieId}`);
    const payload = response.data?.movie ?? response.data;

    if (!payload || typeof payload !== 'object') {
      throw new Error('Resposta invalida ao carregar filme do backend.');
    }

    return mapBackendMovieToMovieDetails(payload as BackendMovieDetails);
  } catch (error: any) {
    throw error;
  }
};

function normalizeComparableText(value: string | null | undefined): string {
  return (value || '').trim().toLowerCase();
}

function sameDate(left: string | null | undefined, right: string | null | undefined): boolean {
  return (left || '') === (right || '');
}

export const findMovieInBackend = async (
  movie: Pick<Movie | MovieDetails, 'title' | 'release_date' | 'overview'>
): Promise<BackendMovieDetails | null> => {
  const normalizedTitle = normalizeComparableText(movie.title);
  const normalizedReleaseDate = movie.release_date || '';

  const findMatch = (candidates: BackendMovieDetails[]) => candidates.find((candidate) => {
    const sameTitle = normalizeComparableText(candidate.title) === normalizedTitle;
    const candidateReleaseDate = candidate.release_date || '';

    return sameTitle && sameDate(candidateReleaseDate, normalizedReleaseDate);
  });

  let page = 1;

  while (page <= 20) {
    const { data } = await api.get<GetMoviesResponse>('/movies', {
      params: {
        per_page: 100,
        page,
        search: movie.title,
      },
    });

    const matchedMovie = findMatch(data.movies || []);

    if (matchedMovie) {
      return matchedMovie;
    }

    const totalPages = data.pagination?.pages ?? page;
    if (page >= totalPages || data.pagination?.has_next === false) {
      break;
    }

    page += 1;
  }

  return null;
};


export const saveRatedMovie = async (
  movie: Movie | MovieDetails,
  rating_user: number,
  userId: string
): Promise<BackendMovieDetails> => {
  const normalizedRating = Math.max(0, Math.min(5, Math.round(rating_user * 2) / 2));
  const formattedDate = movie.release_date || null;
  const posterUrl = movie.poster_path ? getPosterUrl(movie.poster_path, 'w500') : null;
  
  const hasGenres = 'genres' in movie && Array.isArray(movie.genres);
  const serializedGenres = hasGenres
    ? movie.genres.map((genre) => genre.name.trim()).filter(Boolean).join(', ')
    : null;

  const payload = {
    title: movie.title,
    release_date: formattedDate,
    synopsis: movie.overview,
    genre: serializedGenres,
    rating: movie.vote_average, // Rating do TMDB (0-10)
    imgUrl: posterUrl,
    roster: null,
    user_id: userId,
    rating_user: normalizedRating, // Avaliação do usuário (0-5)
  };
  try {
    const response = await api.post('/movies', payload);
    const createdMovie = response.data?.movie;

    if (!createdMovie || typeof createdMovie !== 'object') {
      throw new Error('Resposta invalida ao salvar filme.');
    }

    return createdMovie as BackendMovieDetails;
  } catch (error: any) {
    throw new Error(
      error.response?.data?.message ||
        'Erro ao salvar o filme. Tente novamente.'
    );
  }
};


export const deleteMovie = async (movieId: number): Promise<void> => {
  try {
    await api.delete(`/movies/${movieId}`);
  } catch (error: any) {
    
    throw new Error(
      error.response?.data?.message ||
        'Erro ao deletar o filme. Tente novamente.'
    );
  }
};
