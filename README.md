# 🛡️ NoBadPix – Image Moderation API & Frontend

**NoBadPix** is an image moderation system designed to automatically detect and block harmful or unwanted imagery. It uses a **FastAPI** backend, **MongoDB** for data storage, and the **Azure Content Safety API** for analysis, with a lightweight **HTMX** and **Shoelace UI** frontend.

---

## ⚙️ Tech Stack

- **Backend:** Python, FastAPI
- **Database:** MongoDB
- **Moderation Engine:** Azure Content Safety API
- **Frontend:** HTMX, Shoelace UI

---

## 🚀 Running Locally

1.  **Clone the repository:**
    ```bash
    git clone git@github.com:Arqamz/nobadpix.git
    cd nobadpix
    ```

2.  **Set up your environment:**
    - Create a Python virtual environment and install dependencies:
      ```bash
      python -m venv .venv
      source .venv/bin/activate
      pip install -r requirements.txt
      ```
    - Create a `.env` file by copying the example file:
      ```bash
      cp .env.example .env
      ```
    - Now, edit the `.env` file and provide your specific values.
      The following variables **must be set** by you:
        - `MONGODB_CONNECTION_STRING`: Your full MongoDB connection string.
        - `AZURE_CONTENT_SAFETY_ENDPOINT`: Your Azure Content Safety service endpoint.
        - `AZURE_CONTENT_SAFETY_KEY`: Your Azure Content Safety API key.
        - `SECRET_KEY`: A strong, random secret key for JWT token generation. The one in `.env.example` is a placeholder.

3.  **Run the FastAPI application (from the `nobadpix/` directory):**
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```
    The application will be available at `http://localhost:8000`.

---

## 🐳 Running with Docker

Alternatively, you can run NoBadPix using Docker.

1.  **Build the Docker image:**
    ```bash
    sudo docker build -t nobadpix .
    ```

2.  **Run the Docker container:**
    ```bash
    sudo docker run -d -p 7000:7000 nobadpix
    ```
    The application will then be accessible at `http://localhost:7000`. Please ensure that you have a `.env` file configured as described in the "Running Locally" section, as the Docker build will use it.

---

## 🌐 Live Deployment on Render

You can try out a live version of NoBadPix deployed on Render:

**URL:** [https://nobadpix.onrender.com/](https://nobadpix.onrender.com/)

To test the API (moderating images or using admin features like generating new tokens), you can use the following Bearer token:
`G5CkThwabhcceL3YzXApRgKFA7H8XqjqGDA1g9g2FB8`

---

## 📚 API Endpoints

NoBadPix provides a RESTful API for its operations. For a detailed interactive API documentation, once the application is running (either locally or via the live deployment), please visit:

-   `/docs` for Swagger UI
-   `/redoc` for ReDoc documentation

Key functionalities include:

### 🔐 Authentication (Admin Only)
- Creating new access tokens
- Listing existing tokens
- Revoking tokens

### 🧠 Moderation
- Analyzing uploaded image content

All routes are secured with bearer token authentication. Admin routes require tokens with admin privileges.

---

This project showcases clean architecture, secure API design, and modern frontend techniques.
