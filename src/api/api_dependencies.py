# api/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
import jwt
import logging
from datetime import datetime

from config.database import get_supabase_client as _get_supabase_client
from config.settings import settings

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

def get_supabase_client():
    """Get Supabase client instance"""
    return _get_supabase_client()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: JWT token from Authorization header
        supabase: Supabase client
        
    Returns:
        User information dictionary
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        token = credentials.credentials
        
        # For Supabase, we can verify the token directly
        # In production, you'd use Supabase's built-in auth verification
        
        # Simple JWT verification for demo purposes
        try:
            # Decode without verification for demo
            # In production, use proper JWT verification with Supabase's public key
            payload = jwt.decode(token, options={"verify_signature": False})
            user_id = payload.get("sub")
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
            
            # Get user from database
            user_result = supabase.table("user_profiles")\
                .select("*")\
                .eq("id", user_id)\
                .execute()
            
            if not user_result.data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            user = user_result.data[0]
            
            # Check if user is active/valid
            if not user.get("email"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid user account"
                )
            
            return user
            
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    supabase = Depends(get_supabase_client)
) -> Optional[Dict[str, Any]]:
    """
    Get current user if authenticated, otherwise return None
    Used for endpoints that work with or without authentication
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, supabase)
    except HTTPException:
        return None

def require_subscription_tier(required_tier: str):
    """
    Dependency factory for subscription tier requirements
    
    Args:
        required_tier: Required subscription tier ('free', 'premium', 'pro')
        
    Returns:
        Dependency function
    """
    def check_subscription(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        user_tier = current_user.get("subscription_tier", "free")
        
        tier_hierarchy = ["free", "premium", "pro"]
        
        try:
            user_tier_level = tier_hierarchy.index(user_tier)
            required_tier_level = tier_hierarchy.index(required_tier)
            
            if user_tier_level < required_tier_level:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"This feature requires {required_tier} subscription"
                )
            
            return current_user
            
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid subscription tier"
            )
    
    return check_subscription

def check_generation_credits():
    """
    Check if user has sufficient generation credits
    """
    def verify_credits(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        credits = current_user.get("generation_credits", 0)
        
        if credits <= 0:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Insufficient generation credits"
            )
        
        return current_user
    
    return verify_credits

def require_story_ownership(supabase = Depends(get_supabase_client)):
    """
    Dependency to verify story ownership
    Used in path operations that need story_id
    """
    def verify_ownership(
        story_id: str,
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        try:
            # Check if user owns the story
            result = supabase.table("stories")\
                .select("id, user_id")\
                .eq("id", story_id)\
                .eq("user_id", current_user["id"])\
                .execute()
            
            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Story not found or access denied"
                )
            
            return current_user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ownership verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify story ownership"
            )
    
    return verify_ownership

def require_character_ownership(supabase = Depends(get_supabase_client)):
    """
    Dependency to verify character ownership
    """
    def verify_ownership(
        character_id: str,
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        try:
            result = supabase.table("characters")\
                .select("id, user_id")\
                .eq("id", character_id)\
                .eq("user_id", current_user["id"])\
                .execute()
            
            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Character not found or access denied"
                )
            
            return current_user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Character ownership verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify character ownership"
            )
    
    return verify_ownership

async def get_story_with_access_check(
    story_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Get story and verify user has access
    
    Args:
        story_id: Story ID
        current_user: Current authenticated user
        supabase: Supabase client
        
    Returns:
        Story data
        
    Raises:
        HTTPException: If story not found or access denied
    """
    try:
        result = supabase.table("stories")\
            .select("*")\
            .eq("id", story_id)\
            .eq("user_id", current_user["id"])\
            .execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Story not found or access denied"
            )
        
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get story: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve story"
        )

async def get_chapter_with_access_check(
    story_id: str,
    chapter_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Get chapter and verify user has access through story ownership
    """
    try:
        # First verify story ownership
        story_result = supabase.table("stories")\
            .select("id")\
            .eq("id", story_id)\
            .eq("user_id", current_user["id"])\
            .execute()
        
        if not story_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Story not found or access denied"
            )
        
        # Get chapter
        chapter_result = supabase.table("chapters")\
            .select("*")\
            .eq("id", chapter_id)\
            .eq("story_id", story_id)\
            .execute()
        
        if not chapter_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chapter not found"
            )
        
        return chapter_result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get chapter: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chapter"
        )

def rate_limit(requests_per_minute: int = 60):
    """
    Simple rate limiting dependency
    
    Args:
        requests_per_minute: Maximum requests per minute per user
        
    Returns:
        Dependency function
        
    Note: This is a simple in-memory rate limiter.
    In production, use Redis or similar for distributed rate limiting.
    """
    from collections import defaultdict
    from time import time
    
    # Simple in-memory storage (not suitable for production)
    request_counts = defaultdict(list)
    
    def check_rate_limit(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        user_id = current_user["id"]
        now = time()
        minute_ago = now - 60
        
        # Clean old requests
        request_counts[user_id] = [
            req_time for req_time in request_counts[user_id]
            if req_time > minute_ago
        ]
        
        # Check if user has exceeded rate limit
        if len(request_counts[user_id]) >= requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {requests_per_minute} requests per minute."
            )
        
        # Add current request
        request_counts[user_id].append(now)
        
        return current_user
    
    return check_rate_limit

async def validate_generation_request(
    request_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Validate generation request parameters
    
    Args:
        request_data: Generation request data
        current_user: Current user
        
    Returns:
        Validated request data
        
    Raises:
        HTTPException: If request is invalid
    """
    try:
        # Check word count limits based on subscription
        user_tier = current_user.get("subscription_tier", "free")
        
        word_count_limits = {
            "free": 500,
            "premium": 2000,
            "pro": 5000
        }
        
        max_words = word_count_limits.get(user_tier, 500)
        requested_words = request_data.get("target_word_count", 250)
        
        if requested_words > max_words:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Word count limit exceeded. Maximum for {user_tier}: {max_words} words"
            )
        
        # Validate other parameters
        if requested_words < 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimum word count is 50"
            )
        
        return request_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Request validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request parameters"
        )

# Custom exception handlers
def create_error_response(detail: str, status_code: int = 400) -> HTTPException:
    """Create standardized error response"""
    return HTTPException(
        status_code=status_code,
        detail={
            "error": detail,
            "timestamp": datetime.utcnow().isoformat(),
            "status_code": status_code
        }
    )

# Dependency combinations for common use cases
def require_story_access_with_credits():
    """Combine story access check with credit verification"""
    def combined_check(
        story_id: str,
        current_user: Dict[str, Any] = Depends(check_generation_credits()),
        story: Dict[str, Any] = Depends(get_story_with_access_check)
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        return current_user, story
    
    return combined_check

def require_premium_with_story_access():
    """Combine premium subscription check with story access"""
    def combined_check(
        story_id: str,
        current_user: Dict[str, Any] = Depends(require_subscription_tier("premium")),
        story: Dict[str, Any] = Depends(get_story_with_access_check)
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        return current_user, story
    
    return combined_check

# Utility functions for dependencies
def extract_user_id(current_user: Dict[str, Any]) -> str:
    """Extract user ID from user object"""
    return current_user["id"]

def extract_user_tier(current_user: Dict[str, Any]) -> str:
    """Extract user subscription tier"""
    return current_user.get("subscription_tier", "free")

def extract_user_credits(current_user: Dict[str, Any]) -> int:
    """Extract user generation credits"""
    return current_user.get("generation_credits", 0)

async def consume_generation_credit(
    current_user: Dict[str, Any],
    supabase = Depends(get_supabase_client)
) -> bool:
    """
    Consume one generation credit from user account
    
    Args:
        current_user: Current user
        supabase: Supabase client
        
    Returns:
        True if credit consumed successfully
        
    Raises:
        HTTPException: If insufficient credits or update failed
    """
    try:
        user_id = current_user["id"]
        current_credits = current_user.get("generation_credits", 0)
        
        if current_credits <= 0:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Insufficient generation credits"
            )
        
        # Consume credit
        result = supabase.table("user_profiles")\
            .update({"generation_credits": current_credits - 1})\
            .eq("id", user_id)\
            .execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to consume generation credit"
            )
        
        return True
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to consume credit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Credit consumption failed"
        )
