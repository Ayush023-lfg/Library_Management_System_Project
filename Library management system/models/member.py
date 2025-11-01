from database import Database
from datetime import datetime

class Member:
    def __init__(self):
        self.db = Database()
    
    def add_member(self, name, email, phone=None):
        query = "INSERT INTO members (name, email, phone, membership_date) VALUES (%s, %s, %s, %s)"
        return self.db.execute_query(query, (name, email, phone, datetime.now().date()))
    
    def get_all_members(self):
        query = "SELECT * FROM members ORDER BY created_at DESC"
        return self.db.execute_query(query, fetch=True)
    
    def get_member_by_id(self, member_id):
        query = "SELECT * FROM members WHERE id = %s"
        result = self.db.execute_query(query, (member_id,), fetch=True)
        return result[0] if result else None
    
    def update_member(self, member_id, name, email, phone=None, status=None):
        query = """UPDATE members 
                   SET name = %s, email = %s, phone = %s, status = %s 
                   WHERE id = %s"""
        self.db.execute_query(query, (name, email, phone, status, member_id))
        return True
    
    def delete_member(self, member_id):
        query = "DELETE FROM members WHERE id = %s"
        self.db.execute_query(query, (member_id,))
        return True