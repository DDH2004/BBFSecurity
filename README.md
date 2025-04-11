# Secure AI Assistant

## Overview
The Secure AI Assistant is a FastAPI application designed to provide a private AI-powered knowledge assistant. It utilizes the Gemini API for natural language processing, Midnight for privacy protection, and Auth0 for secure user authentication.

## Features
- **User Authentication**: Secure login and registration using Auth0.
- **AI Interaction**: Users can send queries to the AI assistant and receive intelligent responses.
- **Document Management**: Upload and query personal documents while ensuring privacy through Midnight.

## Project Structure
```
secure-ai-assistant
├── app
│   ├── api
│   │   ├── routes
│   ├── core
│   ├── db
│   ├── services
│   ├── schemas
│   └── utils
├── tests
├── .env
├── .gitignore
├── requirements.txt
└── docker-compose.yml
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd secure-ai-assistant
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables in the `.env` file:
   ```
   AUTH0_DOMAIN=<your-auth0-domain>
   AUTH0_CLIENT_ID=<your-auth0-client-id>
   AUTH0_CLIENT_SECRET=<your-auth0-client-secret>
   GEMINI_API_KEY=<your-gemini-api-key>
   MIDNIGHT_API_KEY=<your-midnight-api-key>
   ```

## Running the Application
To start the FastAPI application, run:
```
uvicorn app.main:app --reload
```

## Testing
To run the tests, use:
```
pytest
```

## License
This project is licensed under the MIT License. See the LICENSE file for details.