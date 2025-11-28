# Backend Assignment

API to fetch latest videos sorted in reverse chronological order of their publishing date-time from YouTube for a given tag/search query in a paginated response.

## Tech-Stack

* Python (Backend Language)
* Django (Python Framework)
* Django REST framework (REST API Toolkit)
* SQLite (Database)

## Features

*   **Video Fetching**: Automatically fetches latest videos for a search query (default: "today news") in the background.
*   **Pagination**: API to list videos with pagination.
*   **Search**: Stores video metadata (Title, Description, Publishing Date, Thumbnail URL).
*   **Dashboard**: Admin dashboard to view stored videos and manage API keys.
*   **Scalability**: Supports multiple API keys with automatic failover when quota is exceeded.

## Instructions

### 1. Setup

*   Clone this repo
*   Create and activate Python Virtual Environment <a href="https://docs.python.org/3/library/venv.html"> (reference) </a>
*   Install dependencies
    > pip install -r requirements.txt

### 2. Database

*   Set up the **database**
    > python manage.py migrate

### 3. Admin User

*   Create superuser to access the dashboard
    > python manage.py createsuperuser

### 4. Running the Server

*   Start the server
    > python manage.py runserver

*   Access the dashboard at:
    > http://127.0.0.1:8000/admin

### 5. Configuration (Crucial Step)

The project requires a valid Google YouTube Data API Key to function. Without it, the background service will not fetch videos, and the API will return an error.

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a project and enable the **YouTube Data API v3**.
3.  Create an API Key.
4.  Add the key to the application via the Admin Dashboard:
    *   Log in to http://127.0.0.1:8000/admin
    *   Go to **Youtube_Api** > **APIKeys**
    *   Click **Add APIKey** and paste your key.
    *   Save.

Alternatively, you can add a key via the API (see below).

## Testing with Postman

A Postman collection is included to help you test the API easily.

1.  **Install Postman**: Download and install [Postman](https://www.postman.com/downloads/).
2.  **Import Collection**:
    *   Open Postman.
    *   Click "Import".
    *   Select the file `youtube_api.postman_collection.json` from the root of this project.
3.  **Use**:
    *   **Get Videos**: Send a GET request to retrieve stored videos.
    *   **Add API Key**: Use the `Add API Key` request. Go to the "Body" tab and replace `"YOUR_API_KEY_HERE"` with your actual Google YouTube API Key before sending.

## API Endpoints

### 1. Get Videos
Returns a paginated list of stored videos sorted by publishing date (descending).

*   **URL**: `/youtube_api/get_videos`
*   **Method**: `GET`
*   **Response**:
    ```json
    {
        "count": 100,
        "next": "http://127.0.0.1:8000/youtube_api/get_videos?page=2",
        "previous": null,
        "results": [
            {
                "title": "Video Title",
                "description": "Video Description",
                "publish_date_time": "2023-10-27T10:00:00Z",
                ...
            }
        ]
    }
    ```

### 2. Add API Key
Add a new YouTube Data API Key.

*   **URL**: `/youtube_api/add_key`
*   **Method**: `POST`
*   **Body**:
    ```json
    {
        "key": "YOUR_API_KEY"
    }
    ```
