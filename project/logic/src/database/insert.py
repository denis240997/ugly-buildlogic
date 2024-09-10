from psycopg2.extras import execute_values
from psycopg2.extensions import register_adapter, AsIs

import pandas as pd
import numpy as np

register_adapter(np.int64, AsIs)
register_adapter(np.int32, AsIs)
register_adapter(np.float64, AsIs)
register_adapter(np.float32, AsIs)
register_adapter(np.bool_, AsIs)

# Из файла csv
def insert_from_csv(cur, csv_file, table_name) -> None:
    # Проверка таблицы на чистоту. Если не чистая, то чистим и загружаем данные
    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cur.fetchone()[0]
        
    if count > 0:
        print(f"Table {table_name} is not empty. Clearing the table before uploading new data.")
        cur.execute(f"TRUNCATE TABLE {table_name} CASCADE")
        print(f"Table {table_name} has been cleared.")
    
    # Столбцы в таблице
    cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}' AND table_schema = 'public'")
    columns = [row[0] for row in cur.fetchall()]

    df = pd.read_csv(csv_file)
    df = df.astype(object).where(pd.notna(df), None)
    
    missing_columns = [col for col in columns if col not in df.columns]
    if missing_columns:
        print(f"Attention! In file {csv_file} missing columns: {', '.join(missing_columns)}")
        print(f"!!!The data from {csv_file} was not uploaded!!!")
        return
    
    records = df[columns].to_records(index=False)
    values = [tuple(record) for record in records]

    query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES %s"
    
    execute_values(cur, query, values)
    print(f"The data from {csv_file} has been uploaded successfully to the table.")


# Ручной ввод
def insert_manually(cur, table_name) -> None:
    # Список столбцов
    cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}' AND table_schema = 'public'")
    columns = [row[0] for row in cur.fetchall()]

    data_to_insert = []

    while True:
        row_data = []
        print(f"\nEnter data for table '{table_name}' (or type 'q' to quit):")
        
        for column in columns:
            value = input(f"Enter value for '{column}': ")
            if value.lower() == 'q':
                if data_to_insert:
                    # Вставляем данные в таблицу
                    placeholders = ", ".join(["%s"] * len(columns))
                    query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                    cur.executemany(query, data_to_insert)
                    print(f"Data successfully inserted into table '{table_name}'.")
                else:
                    print("No data to insert.")
                return
            
            row_data.append(value)

        data_to_insert.append(tuple(row_data))


# Результаты
def insert_results_to_table(cur, operations) -> None:
    # Очистка таблицы результатов 
    cur.execute("DELETE FROM results") 

    # Столбцы из results
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'results' AND table_schema = 'public'")
    columns = [row[0] for row in cur.fetchall()]

    values = []
    for op_id, op in operations.items():
        row_data = [
            op_id,
            op['duration'],
            str(list(op['predecessors'])),
            str(list(op['successors'])),
            str(op['resources']),
            op['early_start'],
            op['early_finish'],
            op['late_start'],
            op['late_finish'],
            op['is_critical']
        ]
        values.append(tuple(row_data))
    
    placeholders = ', '.join(['%s'] * len(columns))
    query = f"INSERT INTO results ({', '.join(columns)}) VALUES ({placeholders})"
    cur.executemany(query, values)

    print(f"Data successfully saved into table 'results'.")
    
    