from typing import Callable
from fastapi import Depends, HTTPException, status

from app.core.roles import UserRole
from app.models.user import User

# IMPORTANT: Adjust this import to match the exact name and location of your 
# existing get_current_user dependency from Module 1/3.
# If it is in app.services.auth_service, change it accordingly.
from app.core.security import get_current_user 


def require_role(required_role: UserRole) -> Callable:
    """
    Dependency factory to enforce Role-Based Access Control (RBAC).
    
    This function returns a dependency that checks if the authenticated 
    user has the exact role required. If not, it raises a 403 Forbidden error.
    
    Usage in routes:
        @router.get("/admin-only", dependencies=[Depends(require_role(UserRole.ADMIN))])
        async def admin_endpoint(current_user: User = Depends(get_current_user)):
            return {"message": f"Hello Admin {current_user.username}"}
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> None:
        # Check if the user's role matches the required role
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role.value}"
            )
    
    return role_checker