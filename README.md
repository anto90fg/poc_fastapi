# FastAPI PySpark Banking API

## Overview
This project is a FastAPI-based banking API that integrates with PySpark for data analysis. It includes authentication, user account management, balance transfers, and transaction analysis.

## Features
- **User Authentication**: OAuth2-based login system with JWT token generation.
- **Account Management**: Retrieve user account details.
- **Balance Transfers**: Transfer funds securely between accounts.
- **Transaction Analysis**: Analyze user transaction history using PySpark.
- **HTML Pages**: Serve login, home, transfer, and analysis pages.

## Technologies Used
- **FastAPI**: Web framework for building APIs.
- **PySpark**: Distributed data processing.
- **JWT**: Token-based authentication.
- **Pydantic**: Data validation.
- **Background Tasks**: Asynchronous logging of transactions.

## Installation
### Prerequisites
- Python 3.8+
- pip
- poetry

### Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/fastapi-pyspark-banking.git
   cd fastapi-pyspark-banking
   ```
2. Install dependencies:
   ```sh
   poetry install
   ```
3. Start the FastAPI server:
   ```sh
   poetry run uvicorn fastapi_webserver.entrypoint:app --host 127.0.0.1 --port 8000 --reload
   ```

## API Endpoints
### Authentication
- **POST `/token`**: Login to get an access token.

### User Management
- **GET `/retrive_user/`**: Retrieve authenticated user details.
- **GET `/account/{username}`**: Get user account balance.

### Transactions
- **POST `/transfer`**: Transfer funds between users.
- **POST `/analyze`**: Analyze transactions using PySpark.

### HTML Pages
- **GET `/`**: Home page.
- **GET `/login`**: Login page.
- **GET `/transfer`**: Transfer funds page.
- **GET `/analyze`**: Transaction analysis page.

## Usage
### 1. Authenticate and Get Token
Use the following `curl` command to log in:
```sh
curl -X POST "http://127.0.0.1:8000/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=test_user&password=pass"
```
Response:
```json
{
  "access_token": "your_jwt_token",
  "token_type": "bearer"
}
```

### 2. Retrieve Account Details
```sh
curl -X GET "http://127.0.0.1:8000/account/test_user" \
     -H "Authorization: Bearer your_jwt_token"
```

### 3. Transfer Funds
```sh
curl -X POST "http://127.0.0.1:8000/transfer" \
     -H "Authorization: Bearer your_jwt_token" \
     -d "receiver=user1&amount=50"
```

### 4. Analyze Transactions
```sh
curl -X POST "http://127.0.0.1:8000/analyze" \
     -H "Authorization: Bearer your_jwt_token"
```

## **Testing**
The application includes automatic tests with **pytest**.
Tests are run using a Docker image.

### **Testing**
``sh
docker compose up
```


## License
This project is licensed under the MIT License.

## Author
Antonio Cervelione - [GitHub](https://github.com/anto90fg)