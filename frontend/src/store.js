import { createStore, applyMiddleware } from 'redux';
import {thunk} from 'redux-thunk'; // Named import
import rootReducer from './reducers'; // Import your root reducer

// Create the store with thunk middleware
const store = createStore(
  rootReducer,
  applyMiddleware(thunk) // Apply thunk middleware
);

export default store;
