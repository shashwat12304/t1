from fastapi import FastAPI, HTTPException, Query
import requests
import time

app = FastAPI()

# ORCID API Credentials
CLIENT_ID = "APP-B3RA9A9LZG7HU5RR"
CLIENT_SECRET = "16c435f3-c7af-40f1-ad24-cdb0755763cc"
TOKEN_URL = "https://orcid.org/oauth/token"
SEARCH_URL = "https://pub.orcid.org/v3.0/search"

# Global token storage (for simplicity; consider a better caching mechanism for production)
token_data = {
    "access_token": None,
    "expires_at": None,
}


def get_access_token():
    """
    Retrieve a valid access token.
    If the current token is expired or unavailable, fetch a new one.
    """
    global token_data

    # Check if the token is still valid
    if token_data["access_token"] and token_data["expires_at"] > time.time():
        return token_data["access_token"]

    # Fetch a new token
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
        "scope": "/read-public",
    }
    headers = {"Accept": "application/json"}

    try:
        response = requests.post(TOKEN_URL, data=data, headers=headers)
        response.raise_for_status()
        token_response = response.json()
        token_data["access_token"] = token_response["access_token"]
        token_data["expires_at"] = time.time() + token_response["expires_in"] - 10  # Buffer time
        return token_data["access_token"]
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to obtain access token: {str(e)}")


@app.get("/search")
def search_author(author_name: str = Query(..., description="Name of the author to search for")):
    """
    Search for an author's ORCID profile by name.
    """
    access_token = get_access_token()

    query = f"name:{author_name}"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    try:
        response = requests.get(f"{SEARCH_URL}?q={query}", headers=headers)
        response.raise_for_status()
        results = response.json().get("result", [])
        if not results:
            return {"message": "No results found for the given author name"}
        return {"search_results": results}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to search ORCID: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
