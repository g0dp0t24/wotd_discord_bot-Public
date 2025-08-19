import sqlite3
from contextlib import closing

database_path = 'hyperlinks.db'  

def delete_entry(entry_id):
    with closing(sqlite3.connect(database_path)) as conn, conn, closing(conn.cursor()) as cursor:
        # Execute the DELETE statement
        cursor.execute('DELETE FROM hyperlinks WHERE id = ?', (entry_id,))
        
        # Commit the changes
        conn.commit()

def delete_entry_cell(sheet_name, cell):
    with closing(sqlite3.connect(database_path)) as conn, conn, closing(conn.cursor()) as cursor:
        # Execute the DELETE statement
        cursor.execute('DELETE FROM hyperlinks WHERE sheet_name = ? AND cell = ?', (sheet_name, cell))
        
        # Commit the changes
        conn.commit()

def update_used_flag(item_identifier):
    with closing(sqlite3.connect(database_path)) as conn, conn, closing(conn.cursor()) as cursor:
        query = '''
        UPDATE hyperlinks
        SET used = 1 
        WHERE text_value IN ({})
        '''.format(','.join('?' for _ in item_identifier))

        cursor.execute(query,item_identifier)
        conn.commit()
        print(f"Updating these items: {item_identifier}")

def random_query():
    with closing(sqlite3.connect(database_path)) as conn, conn, closing(conn.cursor()) as cursor:
        query = '''
        SELECT * FROM hyperlinks WHERE used = 1'''

def edit_table():
    with closing(sqlite3.connect(database_path)) as conn, conn, closing(conn.cursor()) as cursor:
        query = '''
            ALTER TABLE hyperlinks ADD COLUMN processed BOOLEAN DEFAULT 0;
        '''
        cursor.execute(query)
        conn.commit()

if __name__ == "__main__":
    # entry_id_to_delete =   235
    # delete_entry(entry_id_to_delete)
    # print(f"Entry with id {entry_id_to_delete} has been deleted.")
    # sheet_name_to_delete = "2024 :otterly_surprised:"  
    # cell_to_delete = "F28"  
    # delete_entry_cell(sheet_name_to_delete, cell_to_delete)
    # print(f"Entry with sheet name {sheet_name_to_delete} and cell {cell_to_delete} has been deleted.")
    # items_to_update = ["Fastidious", 
    #                    "Aggrieved", 
    #                    "Abdicate", 
    #                    "Tithe", 
    #                    "Aggrandize"]
    # update_used_flag(items_to_update)
    edit_table();