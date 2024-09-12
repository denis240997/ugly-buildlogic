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
    compute_cpm,
    compute_rcpm,
    compute_ssgs,
    compute_rcpm_with_local_sgs,
    get_completion_percentage,
    get_gantt_chart,
    get_gantt_with_resource_chart,
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
            detail=f"Internal Server Error: {e}",
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
            detail=f"Internal Server Error: {e}",
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
            detail=f"Internal Server Error: {e}",
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
            detail=f"Internal Server Error: {e}",
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
            detail=f"Internal Server Error: {e}",
        )


planning_router = APIRouter()


@planning_router.put("/cpm/", status_code=status.HTTP_200_OK)
async def calculate_cpm():
    try:
        result, duration = compute_cpm()
        return {"critical_path": result, "duration": duration}
    except Exception as e:
        log.error(f"Error while calculating CPM: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {e}",
        )


@planning_router.put("/rcpm/", status_code=status.HTTP_200_OK)
async def calculate_rcpm():
    try:
        result, duration = compute_rcpm()
        return {"critical_path": result, "duration": duration}
    except Exception as e:
        log.error(f"Error while calculating RCPM: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {e}",
        )


@planning_router.put("/ssgs/", status_code=status.HTTP_200_OK)
async def calculate_ssgs():
    try:
        result, duration = compute_ssgs()
        return {"critical_path": result, "duration": duration}
    except Exception as e:
        log.error(f"Error while calculating SSGS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {e}",
        )


@planning_router.put("/rcpm_with_local_sgs/", status_code=status.HTTP_200_OK)
async def calculate_rcpm_with_local_sgs(selected_tasks: list[str], use_pr: bool):
    try:
        result, duration = compute_rcpm_with_local_sgs(selected_tasks, use_pr)
        return {"critical_path": result, "duration": duration}
    except Exception as e:
        log.error(f"Error while calculating RCPM with local SGS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {e}",
        )


@planning_router.get("/export-results/", status_code=status.HTTP_200_OK)
async def export_results():
    try:
        output_file = export_table(Table.results)
        return {"download_link": output_file}
    except Exception as e:
        log.error(f"Error while exporting the results: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {e}",
        )


analytics_router = APIRouter()


@analytics_router.get("/completion-percentage/", status_code=status.HTTP_200_OK)
async def completion_percentage():
    try:
        return {"completion_percentage": get_completion_percentage()}
    except Exception as e:
        log.error(f"Error while calculating completion percentage: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {e}",
        )


@analytics_router.get("/gantt-chart/", status_code=status.HTTP_200_OK)
async def gantt_chart():
    try:
        return {"download_link": get_gantt_chart()}
    except Exception as e:
        log.error(f"Error while generating the Gantt chart: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {e}",
        )


@analytics_router.get("/gantt-chart-with-resources/", status_code=status.HTTP_200_OK)
async def gantt_chart_with_resources():
    try:
        return {"download_link": get_gantt_with_resource_chart()}
    except Exception as e:
        log.error(f"Error while generating the Gantt chart with resources: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {e}",
        )
