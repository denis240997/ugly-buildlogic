import psycopg2
import pandas as pd

from config.database_config import host, user, password, dbname, port

from src.database import *
from src.algorithms import *
from src.plot import * 
from src.analytics import *

# Подключение к БД с автокоммитом
def connect_db():
    conn = psycopg2.connect(
        host=host, 
        dbname=dbname, 
        user=user,
        password=password, 
        port=port
    )
    conn.autocommit = True
    return conn

def calculate_cpm(cur, df_operations):
    operations = prepare_operations(df_operations) # Словарь из operations

    critical_path, total_duration = cpm(operations)
    print("Critical Path:", critical_path)
    print("CPM Total Duration of the Project:", total_duration)
    insert_results_to_table(cur, operations)

def calculate_rcpm(cur, df_operations, df_resources):
    operations = prepare_operations(df_operations)

    critical_path, total_duration = rcpm(operations, df_resources)
    print("Critical Path:", critical_path)
    print("RCPM Total Duration of the Project:", total_duration)

    check_resource_conflicts(operations, df_resources) # Проверка конфликт ресурсов
    check_precedence_relations(operations) # Проверка конфликт предшествоания

    insert_results_to_table(cur, operations)

def calculate_ssgs(cur, df_operations, df_resources):
    operations = prepare_operations(df_operations)

    critical_path, total_duration = ssgs(operations, df_resources)
    print("Critical Path:", critical_path)
    print("SSGS Total Duration of the Project:", total_duration)

    check_resource_conflicts(operations, df_resources)
    check_precedence_relations(operations)

    insert_results_to_table(cur, operations)

def calculate_rcpm_with_local_sgs(cur, df_operations, df_resources, selected_tasks, use_pr=False):
    operations = prepare_operations(df_operations)

    critical_path, total_duration = rcpm(operations, df_resources)
    total_duration = local_ssgs(operations, df_resources, selected_tasks, use_pr=use_pr)

    print("Critical Path:", critical_path)
    print("RCPM with local SSGS Total Duration of the Project:", total_duration)

    check_resource_conflicts(operations, df_resources)
    check_precedence_relations(operations)

    insert_results_to_table(cur, operations)

if __name__ == "__main__":

    conn = connect_db()
    cur = conn.cursor()
    
    # Выбрать экран
    scr = input("""Select the screen: 
            1 - Database actions,
            2 - Planner,
            3 - Analytics.
Your choice: """)

    # Совершить выбранное действие на экране
    if scr == "1":
        act = input("""Select the action: 
            1 - create_tables,
            2 - drop_table, 
            3 - drop_all_tables,
            4 - insert_csv,
            5 - insert_manually,
            6 - export_table_to_csv.
Your choice: """)
        
        if act == "1":
            create_tables(cur)

        elif act == "2":
            table_name = input("Enter the table('operations', 'resources', 'additional_info', 'current_status', 'results'): ")
            drop_table(cur, table_name)

        elif act == "3":
            drop_all_tables(cur)

        elif act == "4":
            operations_path = 'test_data/operations.csv'
            resources_path = 'test_data/resources.csv'
            current_status_path ='test_data/current_status.csv'

            insert_from_csv(cur, operations_path, "operations")
            insert_from_csv(cur, resources_path, "resources")
            insert_from_csv(cur, current_status_path, "current_status")

        elif act == "5":
            table = input("Enter table name for manual input ('operations', 'resources', 'additional_info', 'current_status'): ")
            insert_manually(cur, table)
            
        elif act == "6":
            table = "results"
            result_path = "results_output.csv"

            export_table_to_csv(conn, table, result_path)
        else:
            print("Такого действия нет!")

    elif scr == "2":
        act = input("""Select the action: 
            1 - calculate_cpm, 
            2 - calculate_rcpm, 
            3 - calculate_ssgs, 
            4 - calculate_rcpm_with_local_sgs.
Your choice: """)
        
        # Запросы для выполнения планирования
        df_operations = pd.read_sql("SELECT * FROM operations", conn)
        df_resources = pd.read_sql("SELECT * FROM resources", conn)

        if act == "1":
            calculate_cpm(cur, df_operations)

        elif act == "2":
            calculate_rcpm(cur, df_operations, df_resources)

        elif act == "3":
            calculate_ssgs(cur, df_operations, df_resources)

        elif act == "4":
            selected_tasks = [
                        # "TASK1/_/1",
                        # "TASK1/_/2",
                        # "TASK1/_/3",
                        # "TASK2/_/4",
                        "TASK1/_/5",
                        "TASK2/_/6",
                        "TASK3/_/7",
                        "TASK3/_/8",
                        "TASK3/_/9",
                        "TASK4/_/10",
                        "TASK4/_/11",
                        "TASK4/_/12",
                        # "TASK4/_/13",
                        # "TASK4/_/14",
                        # "TASK4/_/15"
                    ]
            calculate_rcpm_with_local_sgs(cur, df_operations, df_resources, selected_tasks)
        else:
            print("Такого действия нет!")
            
    
    elif scr == "3":
        act = input("""Select the action: 
            1 - plot_gantt_chart,         
            2 - plot_gantt_and_resource_chart,
            3 - calculate_completion_percentage,
            4 - detect_project_delays,
            5 - calculate_new_schedule_with_work_not_done.        
Your choice: """)
        df_results = pd.read_sql("SELECT * FROM results", conn)
        df_resources = pd.read_sql("SELECT * FROM resources", conn)
        df_current_status = pd.read_sql("SELECT * FROM current_status", conn)
        df_operations = pd.read_sql("SELECT * FROM operations", conn)

        if act == "1":
            plot_gantt_chart(df_results)
             
        elif act == "2":
            plot_gantt_and_resource_chart(df_results, df_resources)

        elif act == "3":
            calculate_completion_percentage(df_current_status)

        elif act == "4":
            detect_project_delays(df_results, df_current_status)

        elif act == "5":
            completed_tasks = df_current_status[df_current_status['is_done'] == True]['op_id'].tolist()
            df_operations_filtered = df_operations[~df_operations['op_id'].isin(completed_tasks)]
            print(df_operations_filtered)
            algo = input("""Select the algorithm: 
            1 - calculate_cpm, 
            2 - calculate_rcpm, 
            3 - calculate_ssgs.
Your choice: """)
            if algo == "1":
                pass

            elif algo == "2":
                pass

            elif algo == "3":
                pass

            else:
                print("Такого алгоритма нет!") 
        else:
            print("Такого действия нет!")  

    else:
        print("Такого действия нет!")       

    cur.close()
    conn.close()