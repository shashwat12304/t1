from fastapi import FastAPI, Request, Query
import requests

app = FastAPI()

# ORCID API credentials
CLIENT_ID = "APP-B3RA9A9LZG7HU5RR"
CLIENT_SECRET = "16c435f3-c7af-40f1-ad24-cdb0755763cc"
REDIRECT_URI = "http://localhost:8000/auth/callback"
AUTH_URL = "https://orcid.org/oauth/authorize"
TOKEN_URL = "https://orcid.org/oauth/token"
SEARCH_URL = "https://pub.orcid.org/v3.0/search"

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

@app.get("/search")
def search_orcid(author_name: str = Query(..., description="Name of the author to search")):
    """Search for an author's ORCID profile."""
    access_token = get_access_token()
    if not access_token:
        return {"error": "Failed to obtain access token"}

    query = f"name:{author_name}"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(f"{SEARCH_URL}?q={query}", headers=headers)
    if response.status_code == 200:
        results = response.json().get("result", [])
        return {"search_results": results}
    else:
        return {"error": "Failed to search ORCID", "status_code": response.status_code}

def get_access_token():
    """Obtain an access token from ORCID."""
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
        "scope": "/read-public"
    }
    headers = {"Accept": "application/json"}
    response = requests.post(TOKEN_URL, data=data, headers=headers)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
