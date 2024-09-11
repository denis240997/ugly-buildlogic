import logging

from fastapi import APIRouter, HTTPException, status, UploadFile

from app.loader import (
    init_project,
    clear_project,
    Table,
    drop_table_by_name,
    load_table_from_file,
    UploadableTable,
    export_table,
)
from logic.src.database import NotEmptyDBError, IncompatibleColumnsError

log = logging.getLogger("uvicorn")

project_router = APIRouter()


@project_router.post("/create/", status_code=status.HTTP_201_CREATED)
async def create_project():
    try:
        init_project()
        return {"message": "The tables have been created successfully."}
    except NotEmptyDBError as e:  # Backend is busy
        log.error(f"Backend is busy: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Backend is busy! Current user must clear the project to unlock the backend.",
        )
    except Exception as e:
        log.error(f"Error while creating tables: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@project_router.delete("/delete/", status_code=status.HTTP_200_OK)
async def delete_project():
    try:
        clear_project()
        return {"message": "The tables have been deleted successfully."}
    except Exception as e:
        log.error(f"Error while deleting tables: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


tables_router = APIRouter()


@tables_router.post("/upload/", status_code=status.HTTP_201_CREATED)
async def upload_table(file: UploadFile, table_name: UploadableTable):
    try:
        load_table_from_file(file, table_name)
        return {"message": f"The table {table_name} has been uploaded successfully."}
    except IncompatibleColumnsError as e:
        log.error(f"Columns are incompatible: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Columns are incompatible",
        )
    except Exception as e:
        log.error(f"Error while uploading the table {table_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@tables_router.get("/export/", status_code=status.HTTP_200_OK)
async def export_table_to_csv(table_name: Table):
    try:
        output_file = export_table(table_name)
        return {"download_link": output_file}
    except Exception as e:
        log.error(f"Error while exporting the table {table_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@tables_router.delete("/delete/", status_code=status.HTTP_200_OK)
async def delete_table(table_name: Table):
    try:
        drop_table_by_name(table_name)
        return {"message": f"The table {table_name} has been deleted successfully."}
    except Exception as e:
        log.error(f"Error while deleting the table {table_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
