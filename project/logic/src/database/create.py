def create_tables(cur) -> None:   
    # Список таблиц, которые нужно создать
    tables_to_create = {
        'operations': """CREATE TABLE IF NOT EXISTS operations (
                            op_id VARCHAR(255) PRIMARY KEY,
                            duration INT,
                            priority INT,
                            release_time INT,
                            predecessors TEXT,
                            successors TEXT,
                            resources TEXT,
                            deadline INT);""",
                            
        'resources': """CREATE TABLE IF NOT EXISTS resources (
                            type VARCHAR(255) PRIMARY KEY,
                            quantity INT);""",

        'additional_info': """CREATE TABLE IF NOT EXISTS additional_info (
                                info_id VARCHAR(255) PRIMARY KEY,
                                description TEXT);""",

        'current_status': """CREATE TABLE IF NOT EXISTS current_status (
                            op_id VARCHAR(255) PRIMARY KEY,
                            fact_start INT,
                            fact_finish INT,
                            is_done BOOLEAN);""",
                                
        'results': """CREATE TABLE IF NOT EXISTS results (
                            op_id VARCHAR(255) PRIMARY KEY,
                            duration INT,
                            predecessors TEXT,
                            successors TEXT,
                            resources TEXT,
                            early_start INT,
                            early_finish INT,
                            late_start INT,
                            late_finish INT,
                            is_critical BOOLEAN);"""

    }
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ")

    existing_tables = {row[0] for row in cur.fetchall()}
    
    # Создание таблиц, если их нет в БД
    for table_name, query in tables_to_create.items():
        if table_name not in existing_tables:
            cur.execute(query)
            print(f"The table {table_name} has been created successfully.")
        else:
            print(f"!!!The table {table_name} already exist!!!")
    