import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LiaToggleOffSolid } from "react-icons/lia";
import { LiaToggleOnSolid } from "react-icons/lia";

const MovieList = () => {
  const [movies, setMovies] = useState([]);
  const [weekStart, setWeekStart] = useState('');
  const [error, setError] = useState('');
  const [selectedMovie, setSelectedMovie] = useState(null); // State for selected movie
  const [darkMode, setDarkMode] = useState(false); // State for dark mode

  // Function to get the last Friday's date
  function getLastFriday() {
    const d = new Date();
    const dayOfWeek = d.getDay();
    const diff = (dayOfWeek <= 5) ? (dayOfWeek - 5) : (dayOfWeek + 2);
    d.setDate(d.getDate() - diff - 7);
    d.setHours(0, 0, 0, 0); // Set time to 00:00:00
  
    // Format the date as YYYY-MM-DD
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }
  
  console.log(getLastFriday());
  

  // Function to get the Friday date for the next week
  const getNextFriday = () => {
    const d = new Date();
    const dayOfWeek = d.getDay();
    const diff = (dayOfWeek <= 5) ? (dayOfWeek - 5) : (dayOfWeek + 2);
    d.setDate(d.getDate() - diff);
    d.setHours(0, 0, 0, 0); // Set time to 00:00:00
  
    // Format the date as YYYY-MM-DD
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`; // Format as 'YYYY-MM-DD'
  };


  // Fetch movies based on week start date
  const fetchMovies = async (weekStart) => {
    console.log(weekStart)
    try {
      const response = await axios.get('http://127.0.0.1:8000/movies/', {
        params: { week_start: weekStart },
      });
      setMovies(response.data);
    } catch (error) {
      setError('Error fetching movies. Please try again later.');
    }
  };

  // Set the week for This Week's Releases
  const handleThisWeek = () => {
    const lastFridayDate = getLastFriday();
    setWeekStart(lastFridayDate);
    fetchMovies(lastFridayDate);
  };

  // Set the week for Next Week's Releases
  const handleNextWeek = () => {
    const nextFridayDate = getNextFriday();
    setWeekStart(nextFridayDate);
    fetchMovies(nextFridayDate);
  };

  // Initial fetch for the current week on component mount
  useEffect(() => {
    handleThisWeek();
  }, []);

  // Function to handle movie click
  const handleMovieClick = (movie) => {
    setSelectedMovie(movie);
  };

  // Function to close the modal
  const handleCloseModal = () => {
    setSelectedMovie(null);
  };

  // Close modal when clicking outside
  const handleClickOutside = (event) => {
    if (event.target.classList.contains('modal-overlay')) {
      handleCloseModal();
    }
  };

  // Close modal on Esc key press
  const handleEscKey = (event) => {
    if (event.key === 'Escape') {
      handleCloseModal();
    }
  };

  // Add event listeners for click outside and Esc key
  useEffect(() => {
    document.addEventListener('keydown', handleEscKey);
    document.addEventListener('mousedown', handleClickOutside);

    // Cleanup event listeners on component unmount
    return () => {
      document.removeEventListener('keydown', handleEscKey);
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Function to toggle dark mode
  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  return (
    <div className={`pb-10 m-0 w-screen h-screen flex flex-col gap-6 ${darkMode ? 'bg-gray-900 text-gray-100' : 'bg-white text-gray-900'}`}>
      <div className={`flex justify-between items-center sticky top-0 z-20 py-6 px-10 drop-shadow-lg  ${darkMode ? 'bg-gray-900' : 'bg-white'}`}>
        <h1 className="text-3xl font-bold hover:cursor-pointer">CineFav</h1>
        <div className="flex space-x-4 items-center flex-grow justify-center">
          <button
            onClick={handleThisWeek}
            className="p-2 bg-blue-500 text-white rounded hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-300 transition duration-300"
          >
            This Week's Releases
          </button>
          <button
            onClick={handleNextWeek}
            className="p-2 bg-green-500 text-white rounded hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-300 transition duration-300"
          >
            Next Week's Releases
          </button>

        </div>
        <button
          onClick={toggleDarkMode}
          className={`text-3xl transition duration-300`}
        >
          {darkMode ? <LiaToggleOnSolid /> : <LiaToggleOffSolid />}
        </button>
      </div>



      {error && <p className="text-red-500">{error}</p>}

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 w-4/5 mx-auto">
        {movies.length > 0 ? (
          movies.map((movie) => (
            <div
              key={movie._id}
              className="relative group overflow-hidden cursor-pointer rounded-lg"
              onClick={() => handleMovieClick(movie)}
            >
              <img
                src={movie.image_url}
                alt={movie.title || 'Movie'}
                className="w-full h-auto object-cover"
                loading='lazy'
              />
              <div className={`absolute inset-0 bg-black ${darkMode ? 'bg-opacity-60' : 'bg-opacity-50'} opacity-0 group-hover:opacity-75 transition-opacity duration-300 ease-in-out`}></div>
              <div className={`absolute bottom-0 w-full p-4 flex flex-col h-full transition-transform duration-300 ease-in-out transform translate-y-full group-hover:translate-y-0 justify-end text-gray-100`}>
                <h2 className="text-xl font-bold mb-2">
                  {movie.title || 'Movie'}
                </h2>
                <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 ease-in-out">
                  <p className="mb-1">Duration: {movie.duration || 'No Duration'}</p>
                  <p>Genres: {movie.genres.join(', ') || 'Unknown'}</p>
                </div>
              </div>
            </div>
          ))
        ) : (
          <p>No movies found for the selected week.</p>
        )}
      </div>

      {/* Movie Detail Modal */}
      {selectedMovie && (
        <div className={`fixed inset-0 flex items-center justify-center ${darkMode ? 'bg-black bg-opacity-75' : 'bg-gray-900 bg-opacity-75'} z-50 modal-overlay`}>
          <div className={`bg-gray-200 p-6 rounded-lg w-11/12 md:w-3/4 lg:w-2/3 h-[80vh] overflow-y-auto relative flex flex-col md:flex-row ${darkMode ? 'bg-gray-800' : 'bg-gray-200'}`}>
            <img
              src={selectedMovie.image_url}
              alt={selectedMovie.title || 'Movie'}
              className="h-full object-cover rounded-lg mb-4 md:mb-0"
            />
            <div className="w-full md:w-2/3 md:pl-4 flex flex-col items-start">
              <button
                onClick={handleCloseModal}
                className={`text-red-500 hover:text-red-700 text-3xl font-semibold rounded-full ${darkMode ? 'bg-red-100' : 'bg-red-200'} hover:bg-red-200 block w-10 h-10 ml-auto mb-4`}
                aria-label="Close Modal"
              >
                &times;
              </button>
              <div className="w-full md:pl-2 flex flex-col items-start flex-grow">
                <h2 className="text-4xl font-extrabold mb-2">
                  {selectedMovie.title || 'Movie'}
                </h2>
                <p className="mb-1">
                  <span className="font-bold">Duration:</span> {selectedMovie.duration || 'No Duration'}
                </p>
                <p className="mb-1">
                  <span className="font-bold">Genres:</span> {selectedMovie.genres.join(', ') || 'Unknown'}
                </p>
                <p className="mb-1 text-start">
                  <span className="font-bold">Plot:</span> {selectedMovie.plot || 'No Plot Available'}
                </p>
                <p className="mb-1">
                  <span className="font-bold">Director:</span> {selectedMovie.Director || 'Unknown'}
                </p>
                <p className="mb-1">
                  <span className="font-bold">Writers:</span> {selectedMovie.Writers || 'Unknown'}
                </p>
                <p className="mb-1">
                  <span className="font-bold">Stars:</span> {selectedMovie.Stars || 'Unknown'}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MovieList;
