from database import Database
from datetime import datetime, timedelta

class Transaction:
    def __init__(self):
        self.db = Database()
    
    def issue_book(self, book_id, member_id, days=14):
        # Check if book is available
        book_query = "SELECT available_copies FROM books WHERE id = %s"
        book_result = self.db.execute_query(book_query, (book_id,), fetch=True)
        
        if not book_result or book_result[0]['available_copies'] <= 0:
            return False, "Book not available"
        
        issue_date = datetime.now().date()
        due_date = issue_date + timedelta(days=days)
        
        query = "INSERT INTO transactions (book_id, member_id, issue_date, due_date, status) VALUES (%s, %s, %s, %s, 'issued')"
        update_book_query = "UPDATE books SET available_copies = available_copies - 1 WHERE id = %s"
        
        try:
            transaction_id = self.db.execute_query(query, (book_id, member_id, issue_date, due_date))
            self.db.execute_query(update_book_query, (book_id,))
            return True, f"Book issued successfully. Transaction ID: {transaction_id}"
        except Exception as e:
            return False, str(e)
    
    def return_book(self, transaction_id):
        trans_query = "SELECT * FROM transactions WHERE id = %s AND status != 'returned'"
        trans_result = self.db.execute_query(trans_query, (transaction_id,), fetch=True)
        
        if not trans_result:
            return False, "Transaction not found or book already returned"
        
        transaction = trans_result[0]
        return_date = datetime.now().date()
        
        # Calculate fine if overdue
        fine_amount = 0
        if return_date > transaction['due_date']:
            days_overdue = (return_date - transaction['due_date']).days
            fine_amount = days_overdue * 2
        
        update_query = "UPDATE transactions SET return_date = %s, fine_amount = %s, status = 'returned' WHERE id = %s"
        update_book_query = "UPDATE books SET available_copies = available_copies + 1 WHERE id = %s"
        
        try:
            self.db.execute_query(update_query, (return_date, fine_amount, transaction_id))
            self.db.execute_query(update_book_query, (transaction['book_id'],))
            return True, f"Book returned successfully. Fine: ${fine_amount}" if fine_amount > 0 else "Book returned successfully"
        except Exception as e:
            return False, str(e)
    
    def get_all_transactions(self):
        query = """
        SELECT t.*, b.title as book_title, m.name as member_name 
        FROM transactions t
        JOIN books b ON t.book_id = b.id
        JOIN members m ON t.member_id = m.id
        ORDER BY t.created_at DESC
        """
        return self.db.execute_query(query, fetch=True)
    
    def get_overdue_books(self):
        query = """
        SELECT t.*, b.title as book_title, m.name as member_name,
               DATEDIFF(CURDATE(), t.due_date) as days_overdue
        FROM transactions t
        JOIN books b ON t.book_id = b.id
        JOIN members m ON t.member_id = m.id
        WHERE t.due_date < CURDATE() AND t.status = 'issued'
        ORDER BY t.due_date ASC
        """
        return self.db.execute_query(query, fetch=True)