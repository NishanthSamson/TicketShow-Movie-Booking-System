var app = new Vue({
    el: '#app',
    delimiters: ['{', '}'],
    data() {
      return {
        movies: [],
        theatres: [],
        shows: [],
        ushows: [],
        newTheatreName: '',
        newMovieName: '',
        newShowMovieId: '',
        newShowStartTime: '',
        newShowTickets: '',
        selectedFile: null,
        newMovieDesc: '',
        selectedMovie: null,
        selectedDate: null,
        numTickets: 0,
        showAvailableShows: false,
        buttonStatus: 'btn btn-light  ',
      };
    },
    created() {
      this.fetchMovies();
      this.fetchTheatres();
      this.fetchShows()
      this.fetchBookings();
    },
    methods: {
      fetchMovies() {
        axios.get('/api/movies')
          .then(response => {
            this.movies = response.data;
          })
          .catch(error => {
            console.error(error);
          });
      },
      fetchTheatres() {
        axios.get('/api/theaters')
          .then(response => {
            this.theatres = response.data;
          })
          .catch(error => {
            console.error(error);
          });
      },
      fetchShows() {
        axios.get('/api/shows')
          .then(response => {
            this.shows = response.data;
          })
          .catch(error => {
            console.error(error);
          });
      },
      addTheatre() {
        axios.post('/api/add_theatre', {
          theatreName: this.newTheatreName
        })
          .then(response => {
            console.log(response.data);
          })
          .catch(error => {
            console.error(error);
          });
      },
      removeTheatre(TheatreId) {
        axios.post('/api/remove_theatre/', {
          theatreId: TheatreId
        })
          .then(response => {
            console.log(response.data);
          })
          .catch(error => {
            console.error(error);
          });
      },
      addMovie() {
          const formData = new FormData();
          formData.append('movieName', this.newMovieName);
          formData.append('movieDesc', this.newMovieDesc);
          formData.append('file', this.selectedFile);

          axios.post('/api/add_movie', formData)
            .then(response => {
              console.log(response.data);
            })
            .catch(error => {
              console.error(error);
            });
        },
      addShow(TheatreId) {
        axios.post('/api/add_show', {
          showMovieId: this.newShowMovieId,
          startTime: this.newShowStartTime,
          tickets: this.newShowTickets,
          theatreId: TheatreId
        })
          .then(response => {
            console.log(response.data);
          })
          .catch(error => {
            console.error(error);
          });
      },
      removeShow(ShowId) {
        axios.post('/api/remove_show/', {
          showId: ShowId
        })
          .then(response => {
            console.log(response.data);
          })
          .catch(error => {
            console.error(error);
          });
      },
      handleFileChange(event) {
        this.selectedFile = event.target.files[0];
      },
      avshows() {
        axios.post('/api/allshows', {
          movieId: this.selectedMovie,
          date: this.selectedDate,
          numTickets: this.numTickets
        })
          .then(response => {
            this.shows = response.data;
            this.showAvailableShows = true;
          })
          .catch(error => {
            console.error(error);
          });
      },
      bookTickets(ShowId, TheatreId) {
        axios.post('/api/book_tickets', {
          showId: ShowId,
          movieId: this.selectedMovie,
          theatreId: TheatreId,
          numTickets: this.numTickets
        })
          .then(response => {
            console.log(response.data);
          })
          .catch(error => {
            console.error(error);
          });
      },
      fetchBookings() {
        axios.get('/api/my_bookings')
          .then(response => {
            this.ushows = response.data;
          })
          .catch(error => {
            console.error(error);
          });
      }
    }
  });