from fastapi import Depends, HTTPException
from src.db import User
from src.users import current_active_user

def admin_required(user: User = Depends(current_active_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only access")
    return user