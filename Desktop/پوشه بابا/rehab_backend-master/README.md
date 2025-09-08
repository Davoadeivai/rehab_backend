# Rehab Backend

## Project Overview

This project serves as the robust backend system for a rehabilitation center management application. Built with Django, it provides a comprehensive solution for managing patient data, tracking payments, and generating insightful financial reports. The primary goal is to streamline administrative tasks, improve data accuracy, and provide valuable insights into the center's financial health.

## Features

-   **User Authentication and Authorization**: Secure user management system allowing different levels of access (e.g., administrators, staff) with robust authentication and role-based authorization.
-   **Patient Management (CRUD Operations)**: Full Create, Read, Update, and Delete (CRUD) functionalities for patient records, including personal details, medical history, and treatment plans.
-   **Payment Tracking and Management**: Comprehensive system to record, track, and manage patient payments, including payment dates, amounts, and payment periods (weekly, monthly, etc.).
-   **Financial Reporting with Chart.js Visualizations**: Generates dynamic and interactive financial reports using Chart.js, providing visual insights into payment trends, revenue distribution by payment type, and monthly income summaries. This includes:
    -   **Payment Distribution by Type**: A doughnut chart visualizing the proportion of payments based on different payment periods (e.g., weekly, monthly, quarterly).
    -   **Monthly Income Trends**: A bar chart displaying the total income received each month, allowing for easy tracking of financial performance over time.



## Setup

To set up the project locally, follow these steps:

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Davoadeivai/rehab_backend.git
    cd rehab_backend
    ```

2.  **Create a virtual environment and activate it:**

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```
    *(Note: You might need to create a `requirements.txt` file if it doesn't exist, by running `pip freeze > requirements.txt` after installing necessary packages like Django, psycopg2-binary, etc.)*

4.  **Apply database migrations:**

    ```bash
    python manage.py migrate
    ```

5.  **Create a superuser (for admin access):**

    ```bash
    python manage.py createsuperuser
    ```

## Running the Application

To run the Django development server:

```bash
python manage.py runserver
```

The application should now be accessible at `http://127.0.0.1:8000/`.

## Technologies Used

- Django (Python Web Framework)
- PostgreSQL (Database - *assumption, adjust if different*)
- Chart.js (JavaScript charting library)
- HTML/CSS/JavaScript

## Contributing

Feel free to fork the repository and contribute. Please ensure your code adheres to the project's coding standards and includes appropriate tests.

## License

This project is licensed under the MIT License - see the LICENSE file for details. (*Note: Create a LICENSE file if you haven't already*)