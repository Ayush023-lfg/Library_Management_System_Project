from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from models.book import Book
from models.member import Member
from models.transaction import Transaction
from config import Config
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

book_model = Book()
member_model = Member()
transaction_model = Transaction()

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    # Get statistics
    total_books = len(book_model.get_all_books())
    total_members = len(member_model.get_all_members())
    
    # Get issued books count
    all_transactions = transaction_model.get_all_transactions()
    issued_books = len([t for t in all_transactions if t['status'] == 'issued'])
    
    # Get overdue books
    overdue_books = transaction_model.get_overdue_books()
    
    # Get recent transactions (last 5)
    recent_transactions = all_transactions[:5]
    
    stats = {
        'total_books': total_books,
        'total_members': total_members,
        'issued_books': issued_books,
        'overdue_books': len(overdue_books)
    }
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         recent_transactions=recent_transactions,
                         overdue_books=overdue_books,
                         now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# BOOKS ROUTES
@app.route('/books')
def books():
    books = book_model.get_all_books()
    return render_template('books.html', books=books)

@app.route('/books/add', methods=['POST'])
def add_book():
    data = request.form
    try:
        book_model.add_book(
            data['title'],
            data['author'],
            data['isbn'],
            data.get('publisher'),
            data.get('publication_year'),
            data.get('category'),
            int(data.get('total_copies', 1))
        )
        flash('Book added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding book: {str(e)}', 'error')
    return redirect(url_for('books'))

@app.route('/books/update/<int:book_id>', methods=['POST'])
def update_book(book_id):
    data = request.form
    try:
        book_model.update_book(
            book_id,
            data['title'],
            data['author'],
            data['isbn'],
            data.get('publisher'),
            data.get('publication_year'),
            data.get('category'),
            int(data.get('total_copies')) if data.get('total_copies') else None
        )
        flash('Book updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating book: {str(e)}', 'error')
    return redirect(url_for('books'))

@app.route('/books/delete/<int:book_id>')
def delete_book(book_id):
    try:
        book_model.delete_book(book_id)
        flash('Book deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting book: {str(e)}', 'error')
    return redirect(url_for('books'))

@app.route('/books/search')
def search_books():
    search_term = request.args.get('q', '')
    books = book_model.search_books(search_term)
    return jsonify(books)

@app.route('/books/<int:book_id>/json')
def get_book_json(book_id):
    book = book_model.get_book_by_id(book_id)
    if book:
        return jsonify(book)
    return jsonify({'error': 'Book not found'}), 404

# MEMBERS ROUTES
@app.route('/members')
def members():
    members = member_model.get_all_members()
    return render_template('members.html', members=members)

@app.route('/members/add', methods=['POST'])
def add_member():
    data = request.form
    try:
        member_model.add_member(data['name'], data['email'], data.get('phone'))
        flash('Member added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding member: {str(e)}', 'error')
    return redirect(url_for('members'))

@app.route('/members/update/<int:member_id>', methods=['POST'])
def update_member(member_id):
    data = request.form
    try:
        member_model.update_member(
            member_id,
            data['name'],
            data['email'],
            data.get('phone'),
            data.get('status', 'active')
        )
        flash('Member updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating member: {str(e)}', 'error')
    return redirect(url_for('members'))

@app.route('/members/delete/<int:member_id>')
def delete_member(member_id):
    try:
        member_model.delete_member(member_id)
        flash('Member deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting member: {str(e)}', 'error')
    return redirect(url_for('members'))

@app.route('/members/<int:member_id>/json')
def get_member_json(member_id):
    member = member_model.get_member_by_id(member_id)
    if member:
        return jsonify(member)
    return jsonify({'error': 'Member not found'}), 404

# TRANSACTIONS ROUTES
@app.route('/transactions')
def transactions():
    transactions = transaction_model.get_all_transactions()
    books = book_model.get_all_books()
    members = member_model.get_all_members()
    return render_template('transactions.html', 
                         transactions=transactions, 
                         books=books, 
                         members=members)

@app.route('/transactions/issue', methods=['POST'])
def issue_book():
    data = request.form
    success, message = transaction_model.issue_book(
        int(data['book_id']),
        int(data['member_id']),
        int(data.get('days', 14))
    )
    return jsonify({'success': success, 'message': message})

@app.route('/transactions/return/<int:transaction_id>')
def return_book(transaction_id):
    success, message = transaction_model.return_book(transaction_id)
    return jsonify({'success': success, 'message': message})

@app.route('/transactions/overdue')
def overdue_transactions():
    transactions = transaction_model.get_overdue_books()
    return jsonify(transactions)

if __name__ == '__main__':
    app.run(debug=True)