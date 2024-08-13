const initialState = {
    movies: [],
    error: '',
  };
  
  const movieReducer = (state = initialState, action) => {
    switch (action.type) {
      case 'FETCH_MOVIES_SUCCESS':
        return {
          ...state,
          movies: action.payload,
          error: '',
        };
      case 'FETCH_MOVIES_ERROR':
        return {
          ...state,
          error: action.payload,
        };
      default:
        return state;
    }
  };
  
  export default movieReducer;
  