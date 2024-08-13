import axios from 'axios';

export const FETCH_MOVIES_SUCCESS = 'FETCH_MOVIES_SUCCESS';
export const FETCH_MOVIES_ERROR = 'FETCH_MOVIES_ERROR';

const fetchMoviesSuccess = (movies) => ({
  type: FETCH_MOVIES_SUCCESS,
  payload: movies,
});

const fetchMoviesError = (error) => ({
  type: FETCH_MOVIES_ERROR,
  payload: error,
});

export const fetchMovies = (weekStart) => async (dispatch) => {
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/movies/`, {
      params: { week_start: weekStart },
    });
    dispatch(fetchMoviesSuccess(response.data));
  } catch (error) {
    dispatch(fetchMoviesError('Error fetching movies. Please try again later.'));
  }
};
