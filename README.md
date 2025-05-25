# 🛡️ NoBadPix – Image Moderation API & Frontend

**NoBadPix** is a containerized image moderation system designed to automatically detect and block harmful or unwanted imagery such as:

- Graphic violence
- Hate symbols
- Explicit nudity
- Self-harm depictions
- Extremist propaganda

Built using **FastAPI**, it features a secure RESTful API, token-based authentication, MongoDB for tracking and access control, and a lightweight frontend interface built with **HTMX** and **Shoelace UI**. Image analysis is powered by the **Azure Content Safety API**.

---

## ✨ Objectives

- Design a well-structured and secure REST API using FastAPI
- Implement robust token-based authentication and authorization
- Model and track API usage with MongoDB
- Containerize the full stack using Docker
- Build a simple, modern frontend UI to interact with the moderation API
- Follow best practices in code organization, Git workflow, and documentation

---

## ⚙️ Stack Overview

### 🔧 Backend
- **Language:** Python
- **Framework:** FastAPI
- **Auth:** Bearer token-based, with admin-only controls
- **Database:** MongoDB for storing issued tokens and tracking usage
- **Moderation:** Azure Content Safety API

### 🎨 Frontend
- **Tech Stack:** HTMX + Shoelace UI
- **Purpose:** Lightweight dashboard to:
  - Authenticate with token
  - Upload images for moderation
  - Display moderation reports with category and confidence levels

### 📦 Infrastructure
- **Containerized** with Docker
- Optional `docker-compose.yml` for multi-service orchestration
- Git-based workflow (feature branches, PRs, CI hooks)

---

## 📚 API Endpoints

### 🔐 Authentication (Admin Only)
- `POST /auth/tokens` – Create a new token
- `GET /auth/tokens` – List all tokens
- `DELETE /auth/tokens/{token}` – Revoke a specific token

### 🧠 Moderation
- `POST /moderate` – Analyze uploaded image content via Azure API and return a safety report

All routes are secured with bearer token authentication. Admin routes require tokens with `isAdmin: true`.

---

## 🧪 Git Workflow

- `main` — production-ready code
- Feature branches for development and testing
- Code review through pull requests
- CI checks for linting, formatting, and type validation

---

## 🚢 Docker

- FastAPI backend exposed on port `7000`
- Frontend served statically or via an ASGI static mount
- Environment variables provided via `.env` for MongoDB URI and Azure API keys

---

## 🖥️ Frontend Features

- Token input (manual or generated)
- File upload form for image moderation
- Result display with categories and confidence scores
- Styled and responsive UI using Shoelace components

---

This project showcases clean architecture, secure API design, modern frontend techniques without heavy JavaScript tooling, and a full Dockerized development lifecycle.
