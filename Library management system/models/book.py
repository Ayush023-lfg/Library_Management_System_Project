from database import Database

class Book:
    def __init__(self):
        self.db = Database()
    
    def add_book(self, title, author, isbn, publisher=None, publication_year=None, category=None, total_copies=1):
        query = """INSERT INTO books (title, author, isbn, publisher, publication_year, category, total_copies, available_copies)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        return self.db.execute_query(query, (title, author, isbn, publisher, publication_year, category, total_copies, total_copies))
    
    def get_all_books(self):
        query = "SELECT * FROM books ORDER BY created_at DESC"
        return self.db.execute_query(query, fetch=True)
    
    def get_book_by_id(self, book_id):
        query = "SELECT * FROM books WHERE id = %s"
        result = self.db.execute_query(query, (book_id,), fetch=True)
        return result[0] if result else None
    
    def update_book(self, book_id, title, author, isbn, publisher=None, publication_year=None, category=None, total_copies=None):
        # First get current book data to calculate available copies
        current_book = self.get_book_by_id(book_id)
        if not current_book:
            return False
        
        # Calculate new available copies if total copies changed
        if total_copies and total_copies != current_book['total_copies']:
            difference = total_copies - current_book['total_copies']
            new_available = current_book['available_copies'] + difference
        else:
            total_copies = current_book['total_copies']
            new_available = current_book['available_copies']
        
        query = """UPDATE books 
                   SET title = %s, author = %s, isbn = %s, publisher = %s, 
                       publication_year = %s, category = %s, total_copies = %s, 
                       available_copies = %s
                   WHERE id = %s"""
        
        params = (title, author, isbn, publisher, publication_year, category, 
                 total_copies, new_available, book_id)
        
        self.db.execute_query(query, params)
        return True
    
    def delete_book(self, book_id):
        query = "DELETE FROM books WHERE id = %s"
        self.db.execute_query(query, (book_id,))
        return True
    
    def search_books(self, search_term):
        query = "SELECT * FROM books WHERE title LIKE %s OR author LIKE %s OR isbn LIKE %s OR category LIKE %s"
        search_pattern = f"%{search_term}%"
        return self.db.execute_query(query, (search_pattern, search_pattern, search_pattern, search_pattern), fetch=True)