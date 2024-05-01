# TicketShow - Movie Booking System
TicketShow is a multi-user flask based web application which serves as a movie ticket booking system. The app supports Role Based Access Control (RBAC) and provides users
with an intuitive UI for making movie reservations, searching for theatres, and movies. The app uses celery implemented using Redis to implement caching, PDF reports generation and automated
email and newsletter distribution using Celery tasks scheduled via crontab. Admin dashboards are also created to visualize stats and export app data as CSV files.

<h3>Features</h3>
The app features a user-friendly interface and uses bootstrap for the UI, it includes all basic 
features that are present in a movie ticket booking system and also includes additional
features such as a fully customizable user profile, light and dark theme modes and the 
ability to send daily reminders and monthly newsletters to the users of the application.

<h3>API Design</h3>
The app has several API endpoints that allow the client to communicate with the backend.
The movie and theatre APIs are designed to fetch data from the SQLite database.
The book_tickets API allows users to book tickets for a specific show and updates the DB.
The update_profile and proile_pic API allows users to edit and customize their profile.
The my_bookings API fetches and returns user movie bookings.
There are also several APIs for the purpose of adding, removing and editing the details of 
Theatres, movies and shows. The app also has several routes for performing tasks efficiently.

<h3>Screenshots</h3>
<img src="https://raw.githubusercontent.com/NishanthSamson/TicketShow-Movie-Booking-System/main/Screenshots/Screenshot%20(622).png" width="610" height="330"><br>
<img src="https://raw.githubusercontent.com/NishanthSamson/TicketShow-Movie-Booking-System/main/Screenshots/Screenshot%20(623).png" width="610" height="330">
