# Vehicle Parking App (V1)

## Project Overview

This is a multi-user web application designed to manage parking lots, parking spots, and parked vehicles for 4-wheeler parking. It supports two main roles: Admin and regular Users.

## Features

### Admin Role
-   **Root Access**: No registration required (default admin user created programmatically).
-   **Parking Lot Management**: Create, edit, and delete parking lots. (Deletion is only permitted if all spots in the lot are available).
-   **Parking Spot Management**: Parking spots are automatically created based on the `maximum_number_of_spots` defined for a lot. Admin can view the status of all spots within a lot.
-   **User Management**: View all registered users.
-   **Force Release**: Ability to manually release an occupied parking spot if it's stuck or needs admin intervention.

### User Role
-   **Registration/Login**: Users can register and log in to the application.
-   **Parking Spot Reservation**: Choose an available parking lot, and the app automatically allots the first available spot.
-   **Spot Management**: Mark a spot as occupied upon parking and release it upon leaving.
-   **Cost Calculation**: Parking cost is calculated based on duration and lot price.
-   **Reservation History**: View their parking reservation history.

## Technologies Used

-   **Backend**: Flask (Python)
-   **Database**: SQLite
-   **Frontend**: Jinja2 Templating, HTML, CSS (Custom & Bootstrap)
-   **Werkzeug**: For password hashing.

## Setup Instructions

To get the application up and running on your local machine:

1.  **Clone the repository** (if applicable) or ensure all project files are in a single directory.

2.  **Navigate to the project root directory** in your terminal:
    ```bash
    cd /path/to/your/parking_app_directory
    ```

3.  **Install the required Python packages**:
    ```bash
    pip install Flask Flask-SQLAlchemy Werkzeug
    ```

4.  **Delete existing database (if any)**: If you've run the app before and encountered issues, or want a fresh start, delete the `parking_app.db` file from the `instance/` directory. Ensure your Flask app is *not* running when you do this.
    ```bash
    del instance\parking_app.db
    ```
    (On macOS/Linux, use `rm instance/parking_app.db`)

5.  **Run the Flask application**:
    ```bash
    python app.py
    ```

6.  **Access the application**: Open your web browser and go to `http://127.0.0.1:5000/`.

## Default Admin Credentials

Upon first run, an admin user is automatically created if it doesn't exist.

-   **Username**: `admin`
-   **Password**: `admin`

Users can register new accounts via the registration page. 