def drop_table(cur, table_name) -> None:
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    
    tables = cur.fetchall()
    table_names = [table[0] for table in tables]
    
    if table_name in table_names:
        cur.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
        print(f"The table {table_name} has been deleted successfully.")
    else:
        print(f"!!!The table {table_name} was not founded in the database!!!")


def drop_all_tables(cur) -> None:
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ")
    tables = cur.fetchall()

    if not tables:
        print("!!!There are no tables in the database!!!")
        return

    for table_name in tables:
        cur.execute(f"DROP TABLE IF EXISTS {table_name[0]} CASCADE")
        print(f"The table {table_name[0]} has been deleted successfully.")