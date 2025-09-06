"""
SSO-based authentication and authorization module.

This module provides SSO integration for the FastAPI application,
supporting various SSO providers and token validation.
"""

import os
import httpx
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)

# Initialize HTTP Bearer security scheme
security = HTTPBearer()

class SSOAuth:
    """
    SSO Authentication handler for various SSO providers.
    """
    
    def __init__(self):
        self.sso_endpoint = os.getenv("SSO_ENDPOINT", "https://your-sso-provider.com")
        self.sso_client_id = os.getenv("SSO_CLIENT_ID")
        self.sso_client_secret = os.getenv("SSO_CLIENT_SECRET")
        self.token_validation_endpoint = f"{self.sso_endpoint}/validate"
        self.user_info_endpoint = f"{self.sso_endpoint}/userinfo"
        
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate SSO token with the SSO provider.
        
        Args:
            token: The bearer token to validate
            
        Returns:
            Dict containing user information if token is valid
            
        Raises:
            HTTPException: If token validation fails
        """
        try:
            logger.info("Validating SSO token")
            
            # Make request to SSO provider for token validation
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                # Validate token
                response = await client.get(
                    self.token_validation_endpoint,
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    logger.info("SSO token validation successful")
                    return token_data
                else:
                    logger.warning(f"SSO token validation failed: {response.status_code}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid or expired token"
                    )
                    
        except httpx.TimeoutException:
            logger.error("SSO token validation timeout")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="SSO service unavailable"
            )
        except Exception as e:
            logger.error(f"SSO token validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token validation failed"
            )
    
    async def get_user_info(self, token: str) -> Dict[str, Any]:
        """
        Get user information from SSO provider.
        
        Args:
            token: The bearer token
            
        Returns:
            Dict containing user information
        """
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                response = await client.get(
                    self.user_info_endpoint,
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Failed to get user info: {response.status_code}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return {}

# Initialize SSO auth instance
sso_auth = SSOAuth()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user.
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        Dict containing user information
        
    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    try:
        # Validate token with SSO provider
        token_data = await sso_auth.validate_token(credentials.credentials)
        
        # Get additional user information
        user_info = await sso_auth.get_user_info(credentials.credentials)
        
        # Combine token data and user info
        user_data = {
            "token_data": token_data,
            "user_info": user_info,
            "token": credentials.credentials
        }
        
        logger.info(f"User authenticated: {user_info.get('email', 'unknown')}")
        return user_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    Optional authentication dependency for endpoints that can work with or without auth.
    
    Args:
        credentials: Optional HTTP Bearer credentials
        
    Returns:
        Dict containing user information if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None

def require_permissions(required_permissions: list):
    """
    Decorator to require specific permissions for endpoints.
    
    Args:
        required_permissions: List of required permissions
        
    Returns:
        Decorator function
    """
    def permission_checker(user: Dict[str, Any] = Depends(get_current_user)):
        user_permissions = user.get("user_info", {}).get("permissions", [])
        
        if not all(perm in user_permissions for perm in required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        return user
    
    return permission_checker

def require_role(required_role: str):
    """
    Decorator to require specific role for endpoints.
    
    Args:
        required_role: Required role name
        
    Returns:
        Decorator function
    """
    def role_checker(user: Dict[str, Any] = Depends(get_current_user)):
        user_role = user.get("user_info", {}).get("role")
        
        if user_role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role privileges"
            )
        
        return user
    
    return role_checker

# Example usage in routes:
# @router.get("/protected")
# async def protected_endpoint(user: Dict[str, Any] = Depends(get_current_user)):
#     return {"message": f"Hello {user['user_info'].get('name', 'User')}"}

# @router.get("/admin-only")
# async def admin_endpoint(user: Dict[str, Any] = Depends(require_role("admin"))):
#     return {"message": "Admin access granted"}

# @router.get("/permission-required")
# async def permission_endpoint(user: Dict[str, Any] = Depends(require_permissions(["read:dns", "write:dns"]))):
#     return {"message": "Permission-based access granted"}
