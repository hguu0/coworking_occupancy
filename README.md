# Coworking Occupancy Predictor

A web application for booking coworking spaces and monitoring their occupancy levels using historical data analysis.

**Live Demo:** [https://coworking-occupancy.pythonanywhere.com](https://coworking-occupancy.pythonanywhere.com)

## Technologies
*   **Python 3.13**
*   **Django 4.2**
*   **Pandas & Matplotlib** (Data Analysis & Visualization)
*   **Tailwind CSS** (UI Styling)

## Features
*   **Space Listing:** View available coworking zones with amenities and pricing.
*   **Booking System:** Registered users can book spaces for specific time slots.
*   **Occupancy Analytics:** Visual graphs showing historical occupancy trends to help with planning.
*   **Admin Dashboard:** Manage spaces, amenities, and view logs.

## Screenshots
![Home Page](static/screenshots/home.png)
*List of coworking spaces*

![Space Details](static/screenshots/detail.png)
*Space details with occupancy graph*

## Local Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd coworking_occupancy
    ```

2.  **Create and activate virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/Mac
    # .venv\Scripts\activate   # Windows
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run migrations:**
    ```bash
    python manage.py migrate
    ```

5.  **Seed data (Optional):**
    ```bash
    # Run the seed script via shell
    echo "exec(open('seed_script.py').read())" | python manage.py shell
    ```

6.  **Start the server:**
    ```bash
    python manage.py runserver
    ```

7.  **Access the app:**
    Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

## Deployment
This project is configured for deployment on PythonAnywhere.
1.  Clone repo on server.
2.  Install requirements.
3.  Run migrations & collectstatic.
4.  Configure WSGI file.
