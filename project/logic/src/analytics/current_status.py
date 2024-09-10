import pandas as pd
from datetime import datetime

def calculate_completion_percentage(df_current_status) -> None:
    completed_tasks = df_current_status['is_done'].sum()
    total_tasks = len(df_current_status)
    # процент работ завершенных
    completion_percentage = (completed_tasks / total_tasks) * 100 
    print(f"Percentage of completed works: {completion_percentage}%")  


def detect_project_delays(df_results, df_current_status) -> None:
    df_merged = pd.merge(df_results, df_current_status, on='op_id', how='left')

    mismatches = df_merged[
        (df_merged['is_done'] == True) & 
        ((df_merged['early_start'] != df_merged['fact_start']) | 
        (df_merged['early_finish'] != df_merged['fact_finish']))
    ]

    if not mismatches.empty:
        print("Mismatches found between planned and actual dates for completed tasks:")
        print(mismatches[['op_id', 'early_start', 'fact_start', 'early_finish', 'fact_finish']])
    else:
        print("All actual dates for completed tasks match the planned dates.")