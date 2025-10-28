from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import jwt
from dotenv import load_dotenv
import httpx
import os, json, time, uuid

load_dotenv()

# Environment variables
CLIENT_ID = os.getenv("ZITADEL_CLIENT_ID")
TOKEN_URL = os.getenv("ZITADEL_TOKEN_URL")
JWK_PATH = os.getenv("ZITADEL_JWK_PATH")
ZITADEL_ISSUER = os.getenv("ZITADEL_ISSUER")
ZITADEL_JWKS_URL = os.getenv("ZITADEL_JWKS_URL")

app = FastAPI(
    title="Zitadel Multi-Tenant Demo",
    swagger_ui_init_oauth={
        "clientId": CLIENT_ID,
        "usePkceWithAuthorizationCodeGrant": True,
        "scopes": "openid profile email",
    }
)

# Add this right after loading CLIENT_ID
print(f"🔑 CLIENT_ID loaded: {CLIENT_ID}")

# OAuth2 scheme for Swagger UI
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{ZITADEL_ISSUER}/oauth/v2/authorize",
    tokenUrl=TOKEN_URL,
    scopes={
        "openid": "OpenID Connect",
        "profile": "User profile information",
        "email": "User email address",
    }
)

# Function to get JWKS (public keys for verification)
async def get_jwks():
    async with httpx.AsyncClient() as client:
        response = await client.get(ZITADEL_JWKS_URL)
        return response.json()

# Verify the token
# Update your verify_token function
async def verify_token(token: str = Depends(oauth2_scheme)):
    print(f"🎫 Received token: {token[:50]}...")  # Print first 50 chars
    try:
        jwks = await get_jwks()
        # Decode without verification first to get the key ID
        if token.count(".") != 2:
            print("⚠️ This is not a JWT — Zitadel returned an opaque access token.")
            raise HTTPException(
            status_code=401,
            detail="Received opaque token. You need to request ID token instead of access token.",
        )

        unverified_header = jwt.get_unverified_header(token)
        print(f"📋 Token header: {unverified_header}")
        
        # Find the right key
        rsa_key = None
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = key
                break
        
        if not rsa_key:
            raise HTTPException(status_code=401, detail="Invalid token - key not found")
        
        # Verify and decode
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=CLIENT_ID,
            issuer=ZITADEL_ISSUER
        )
        return payload
    except Exception as e:
        print(f"❌ Token verification error: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    
# Your existing /token endpoint
@app.get("/token")
async def get_token():
    return JSONResponse(content={"message": "Token endpoint"})

# Protected endpoint
@app.get("/protected")
async def protected_route(token_data: dict = Depends(verify_token)):
    return {
        "message": "You are authenticated!",
        "user_id": token_data.get("sub"),
        "email": token_data.get("email"),
        "full_token_data": token_data  # See all claims for debugging
    }

# Health check
@app.get("/")
async def root():
    return {"message": "Zitadel Multi-Tenant API is running"}


