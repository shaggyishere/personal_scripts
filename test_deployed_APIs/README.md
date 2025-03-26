# API Tester

## 📌 Overview
This script is designed to **test a suite of deployed APIs** from a given `BASE_URL`. It automates the following steps before executing API tests:
1. **Retrieve a JWT token** from an authentication endpoint.
2. **Create a session** to handle multiple API requests efficiently.
3. **Execute API requests** (GET, POST, PUT, etc.) as specified in the `apis_to_test.json` file.
4. **Log responses**, store JSON responses in a file, and track API response statuses.

---

## ⚙️ Installation
### **1️⃣ Install Dependencies using `requirements.txt`**
```bash
pip install -r requirements.txt
```

---

## 🌍 Setting Up Environment Variables
This script requires a `.env` file containing necessary configurations. Create a `.env` file in the project root with the following variables:

#### **📌 `.env` Configuration**
```ini
BASE_URL=https://api.example.com
AUTH_URL=https://auth.example.com
SESSION_MANAGER_URL=https://session.example.com

AUTH_PAYLOAD={"username": "user", "password": "pass"}
SESSION_MANAGER_PAYLOAD={"session_id": "12345"}

AUTH_BASIC_AUTH_HEADER=Basic dXNlcm5hbWU6cGFzc3dvcmQ=
```

These variables define:
- **`BASE_URL`** → The base URL for all API tests.
- **`AUTH_URL`** → The endpoint to obtain a JWT token.
- **`SESSION_MANAGER_URL`** → The session management endpoint.
- **`AUTH_PAYLOAD`** → The authentication request body (JSON format as a string).
- **`SESSION_MANAGER_PAYLOAD`** → The session manager request body.
- **`AUTH_BASIC_AUTH_HEADER`** → Base64-encoded basic authentication header.

---

## 📋 Configuring API Tests
### **2️⃣ Modify `apis_to_test.json` to Specify API Endpoints**
The script dynamically loads API test configurations from `apis_to_test.json`. This file must be modified to specify which APIs should be tested.

#### **Example `apis_to_test.json`**
```json
[
  {
    "method": "GET",
    "route": "/users",
    "headers": {"Accept": "application/json"},
    "query_params": {"status": "active"}
  },
  {
    "method": "POST",
    "route": "/login",
    "body": {"username": "test", "password": "1234"}
  }
]
```

- **`method`** → HTTP method (`GET`, `POST`, `PUT`, etc.)
- **`route`** → API route (relative to `BASE_URL`)
- **`params`** → Query parameters (for `GET` requests)
- **`body`** → JSON payload (for `POST/PUT` requests)

#### **⚠️ Avoid Committing `apis_to_test.json`**
If you plan to contribute to the source code, remember to **avoid staging `apis_to_test.json` for commits** by running the following command locally:
```bash
git update-index --assume-unchanged ./apis_to_test.json
```
This ensures your local modifications to the test API file don’t get committed accidentally.

---

## 🚀 Running the API Tester
Once dependencies are installed and configurations are set up, you can run the script:
```bash
python api_tester.py
```

---

## 📂 Output
- **JSON responses** will be saved into a file.
- **HTTP status codes** will be logged to track API availability.
- **Detail infos, errors and failures** will be displayed in the console and in a log file.

---

## 🛠 Troubleshooting
- **Missing `.env` File:** Ensure the `.env` file exists before running the script.
- **JSON Parsing Issues:** Ensure `apis_to_test.json` is properly formatted.

---

## 📜 License
This project is **open-source**.
