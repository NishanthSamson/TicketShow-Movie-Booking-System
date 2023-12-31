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
        newShowPrice: 0,
        selectedFile: null,
        newMovieDesc: '',
        newMovieGenre: '',
        newMovieRating: 0,
        selectedMovie: null,
        selectedDate: null,
        numTickets: 0,
        showAvailableShows: false,
        buttonStatus: 'btn btn-light',
        loggedIn: false,
        loginDisp: false,
        loading: true,
        uname: '',
        uphone: '',
        ugender: '',
        uaddress: '',
        profilepic: null,
        theme: 'dark',
        manageTheatre: '',
        queryString: '',
        searchResults: [],
        showSearchResults: true,
        theatreName: '',
        movieName: '',
        movieDesc: '',
      };
    },
    created() {
      this.fetchData();
    },
    methods: {
      fetchData() {
        Promise.all([
          this.fetchMovies(),
          this.fetchTheatres(),
          // this.fetchShows(),
          this.fetchBookings(),
        ])
          .then(() => {
            this.loading = false;
          })
          .catch(error => {
            console.error(error);
          });
      },
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
      addTheatre() {
        const formData = new FormData();

        formData.append('theatreName', this.newTheatreName);
        formData.append('theatreDesc', this.newTheatreDesc);
        formData.append('file', this.selectedFile);

        axios.post('/api/add_theatre', formData)
          .then(response => {
            console.log(response.data);
          })
          .catch(error => {
            console.error(error);
          });
      },
      editTheatre(TheatreId) {
        axios.post('/api/edit_theatre', {
          theatreId: TheatreId,
          theatreName: this.theatreName,
        })
          .then(response => {
            console.log(response.data);
          })
          .catch(error => {
            console.error(error);
          });
      },
      removeTheatre(TheatreId) {
        axios.post('/api/remove_theatre', {
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
          formData.append('movieGenre', this.newMovieGenre);
          formData.append('movieRating', this.newMovieRating);
          formData.append('file', this.selectedFile);

          axios.post('/api/add_movie', formData)
            .then(response => {
              console.log(response.data);
            })
            .catch(error => {
              console.error(error);
            });
        },
        editMovie(MovieId) {
          axios.post('/api/edit_movie', {
            movieId: MovieId,
            movieName: this.movieName,
            movieDesc: this.movieDesc,
          })
            .then(response => {
              console.log(response.data);
            })
            .catch(error => {
              console.error(error);
            });
        },
        removeMovie(MovieId) {
          axios.post('/api/remove_movie', {
            movieId: MovieId
          })
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
          price: this.newShowPrice,
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
        axios.post('/api/remove_show', {
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
      handleProfileChange(event) {
        this.profilepic = event.target.files[0];
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
      },
      updateProfile() {
        axios.post('/api/update_profile', {
          uName: this.uname,
          uPhone: this.uphone,
          uGender: this.ugender,
          uAddress: this.uaddress
        })
          .then(response => {
            console.log(response.data);
          })
          .catch(error => {
            console.error(error);
          });
      },
      profilePic() {
        const formData = new FormData();
        formData.append('file', this.profilepic);

        axios.post('/api/profilepic', formData)
          .then(response => {
            console.log(response.data);
          })
          .catch(error => {
            console.error(error);
          });
      },
      toggleTheme() {
        if (this.theme === 'dark') {
          this.theme = 'light';
          document.documentElement.setAttribute('data-bs-theme', 'light');
        } else {
          this.theme = 'dark';
          document.documentElement.setAttribute('data-bs-theme', 'dark');
        }
      },
        getMovieURL(movieId) {
          return `/movie/${movieId}/view/`;
        },
        getTheatreURL(theatreId) {
          return `/theatre/${theatreId}/view/`;
        },
        exportCSV(theatreId) {
          window.location.href = `/export_theatre_csv/${theatreId}`;
        },
        bookMovie(movieId) {
          this.selectedMovie = movieId;
        },
        manageShows(theatreId) {
          this.manageTheatre = theatreId;
          const url = `/admin/manage/${theatreId}`;
          window.location.href = url;
        },
        redirectToResults() {
          if (this.queryString.trim() !== '') {
            const url = `/search/results?query=${encodeURIComponent(this.queryString)}`;
            window.location.href = url;
          }
        },
    }
  });