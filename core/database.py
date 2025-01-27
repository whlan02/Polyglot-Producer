import sqlite3


class DatabaseManager:
    def __init__(self, learning_language):

        self.db_name = f"knowledge_graph_{learning_language}.db"
        self.connection = sqlite3.connect(self.db_name)
        print(f"Connected to database '{self.db_name}'.")
        self.create_tables()

    def create_tables(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_lang TEXT NOT NULL,
                base_lang TEXT NOT NULL,
                group_id INTEGER,
                group_name TEXT NOT NULL,
                FOREIGN KEY (group_id) REFERENCES groups (id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER,
                related_item_id INTEGER,
                relation_name TEXT,
                FOREIGN KEY (item_id) REFERENCES items (id),
                FOREIGN KEY (related_item_id) REFERENCES items (id)
            )
        """)
        self.connection.commit()
        print("Tables have been created successfully.")

    def add_item(self, target_lang, base_lang, group_id, group_name):
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO items (target_lang, base_lang, group_id, group_name)
            VALUES (?, ?, ?, ?)
        """, (target_lang, base_lang, group_id, group_name))
        self.connection.commit()

    def add_group(self, group_name):
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO groups (name) VALUES (?)", (group_name,))
        self.connection.commit()

    def delete_group(self, group_name):
        cursor = self.connection.cursor()
        try:

            cursor.execute("SELECT id FROM groups WHERE name = ?", (group_name,))
            group_id_result = cursor.fetchone()
            if not group_id_result:
                raise ValueError(f"Group '{group_name}' does not exist.")
            
            group_id = group_id_result[0]
            

            cursor.execute("DELETE FROM groups WHERE id = ?", (group_id,))
            

            cursor.execute("DELETE FROM items WHERE group_id = ?", (group_id,))
            
            self.connection.commit()
            print(f"Group '{group_name}' and its items have been deleted from the database.")
        except Exception as e:
            self.connection.rollback()
            print(f"Error deleting group: {e}")

    def delete_item(self, base_lang, group_name):
        cursor = self.connection.cursor()
        try:

            cursor.execute("SELECT id FROM groups WHERE name = ?", (group_name,))
            group_id_result = cursor.fetchone()
            if not group_id_result:
                raise ValueError(f"Group '{group_name}' does not exist.")
            
            group_id = group_id_result[0]
            

            cursor.execute("SELECT id FROM items WHERE base_lang = ? AND group_id = ?", (base_lang, group_id))
            item_id_result = cursor.fetchone()
            if not item_id_result:
                raise ValueError(f"Item '{base_lang}' in group '{group_name}' does not exist.")
            
            item_id = item_id_result[0]
            

            cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
            
            self.connection.commit()
            print(f"Item '{base_lang}' in group '{group_name}' has been deleted from the database.")
        except Exception as e:
            self.connection.rollback()
            print(f"Error deleting item: {e}")

    def add_relation_table(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER,
                related_item_id INTEGER,
                relation_name TEXT,
                FOREIGN KEY (item_id) REFERENCES items (id),
                FOREIGN KEY (related_item_id) REFERENCES items (id)
            )
        """)
        self.connection.commit()
    

    def get_items_by_group_name(self, group_name):
        cursor = self.connection.cursor()

        cursor.execute("SELECT id FROM groups WHERE name = ?", (group_name,))
        group_id_result = cursor.fetchone()
        if not group_id_result:
            return []  

        group_id = group_id_result[0]

        cursor.execute("""
            SELECT target_lang, base_lang
            FROM items
            WHERE group_id = ?
        """, (group_id,))
        items = cursor.fetchall()

   
        items_list = [{"target_lang": item[0], "base_lang": item[1]} for item in items]
        return items_list