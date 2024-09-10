import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

log = logging.getLogger("uvicorn")

router = APIRouter()


@router.get("/me/")
async def read_users_me():
    """Get current user details"""
    return {"user": "user"}
