import logging

from fastapi import APIRouter, HTTPException, status

from app.loader import init_project, clear_project
from logic.src.database import NotEmptyDBError

log = logging.getLogger("uvicorn")

router = APIRouter()


@router.post("/create-project/", status_code=status.HTTP_201_CREATED)
async def create_project():
    try:
        init_project()
        return {"message": "The tables have been created successfully."}
    except NotEmptyDBError as e: # Backend is busy
        log.error(f"Backend is busy: {e}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Backend is busy! Current user must clear the project to unlock the backend.")
    except Exception as e:
        log.error(f"Error while creating tables: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal Server Error")


@router.delete("/delete-project/", status_code=status.HTTP_200_OK)
async def delete_project():
    try:
        clear_project()
        return {"message": "The tables have been deleted successfully."}
    except Exception as e:
        log.error(f"Error while deleting tables: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal Server Error")
