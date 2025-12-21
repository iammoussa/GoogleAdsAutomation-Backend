# -*- coding: utf-8 -*-
"""
Shared API Dependencies
"""

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify JWT token
    
    TODO: Implement proper JWT verification with:
    - Token decoding
    - Expiration check
    - User validation
    
    For now, accept any token for development
    """
    if not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    # TODO: Decode and verify JWT token
    # from jose import jwt, JWTError
    # try:
    #     payload = jwt.decode(
    #         credentials.credentials,
    #         SECRET_KEY,
    #         algorithms=["HS256"]
    #     )
    #     user_id = payload.get("sub")
    #     if user_id is None:
    #         raise HTTPException(status_code=401, detail="Invalid token")
    #     return user_id
    # except JWTError:
    #     raise HTTPException(status_code=401, detail="Invalid token")
    
    # For development, return token as-is
    return credentials.credentials
