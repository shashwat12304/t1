from fastapi import FastAPI, Request
import requests

app = FastAPI()

# ORCID API Credentials
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
REDIRECT_URI = "http://localhost:8000/auth/callback"
AUTH_URL = "https://orcid.org/oauth/authorize"
TOKEN_URL = "https://orcid.org/oauth/token"

@app.get("/")
def home():
    """Welcome page with link to ORCID authorization."""
    auth_link = (
        f"{AUTH_URL}?client_id={CLIENT_ID}&response_type=code"
        f"&scope=/read-public&redirect_uri={REDIRECT_URI}"
    )
    return {"message": "Welcome! Click the link to authorize:", "auth_link": auth_link}

@app.get("/auth/callback")
def auth_callback(request: Request):
    """Handle ORCID's Redirect with the authorization code."""
    auth_code = request.query_params.get("code")
    if not auth_code:
        return {"error": "No authorization code provided"}

    # Exchange the authorization code for an access token
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
    }
    headers = {"Accept": "application/json"}
    response = requests.post(TOKEN_URL, data=data, headers=headers)
    if response.status_code == 200:
        token_data = response.json()
        return {"access_token": token_data["access_token"], "token_type": token_data["token_type"]}
    else:
        return {"error": "Failed to exchange code for token", "status_code": response.status_code}
