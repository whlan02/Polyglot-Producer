class RelationManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def add_relation(self, item_id, related_item_id, relation_name):
        cursor = self.db_manager.connection.cursor()
        cursor.execute("""
            INSERT INTO relations (item_id, related_item_id, relation_name)
            VALUES (?, ?, ?)
        """, (item_id, related_item_id, relation_name))
        self.db_manager.connection.commit()

    def get_relations(self, item_id):
        cursor = self.db_manager.connection.cursor()
        cursor.execute("""
            SELECT related_item_id, relation_name FROM relations
            WHERE item_id = ?
        """, (item_id,))
        return cursor.fetchall()
