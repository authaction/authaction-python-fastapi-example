# FastAPI + AuthAction Integration

This is a FastAPI application that integrates with AuthAction for OAuth2 authentication.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the root directory with the following variables:
```env
# AuthAction Configuration
AUTHACTION_CLIENT_ID=your_client_id_here
AUTHACTION_CLIENT_SECRET=your_client_secret_here
AUTHACTION_REDIRECT_URI=http://localhost:8000/auth/callback
AUTHACTION_DOMAIN=your-authaction-domain.com

# Session Secret (change this to a secure random string)
SESSION_SECRET_KEY=your-secret-key-here
```

3. Update the session secret in `app/main.py`:
```python
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY", "your-secret-key-here"))
```

## Running the Application

```bash
uvicorn app.main:app --reload
```

## Endpoints

- `GET /auth/login` - Initiates OAuth2 login flow
- `GET /auth/callback` - OAuth2 callback endpoint

## Common Issues Fixed

1. **Internal Server Error**: The application now includes proper error handling and session middleware
2. **Missing Environment Variables**: The app checks for required environment variables and provides clear error messages
3. **Session Handling**: Fixed session access and added proper middleware
4. **HTTP Error Handling**: Added proper exception handling for HTTP requests

## Troubleshooting

If you're still getting internal server errors:

1. Make sure all environment variables are set in your `.env` file
2. Check that your AuthAction domain is correct
3. Verify your client ID and client secret are valid
4. Ensure the redirect URI matches what's configured in your AuthAction application 