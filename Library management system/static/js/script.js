document.addEventListener('DOMContentLoaded', function() {
    // Books search
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    
    if (searchInput && searchButton) {
        searchButton.addEventListener('click', performSearch);
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
    }
    
    // Book return functionality
    const returnButtons = document.querySelectorAll('.return-btn');
    returnButtons.forEach(button => {
        button.addEventListener('click', function() {
            const transactionId = this.getAttribute('data-transaction-id');
            returnBook(transactionId);
        });
    });
    
    // Issue book form
    const issueBookForm = document.getElementById('issueBookForm');
    if (issueBookForm) {
        issueBookForm.addEventListener('submit', function(e) {
            e.preventDefault();
            issueBook();
        });
    }
    
    // View overdue transactions
    const viewOverdueBtn = document.getElementById('viewOverdueBtn');
    if (viewOverdueBtn) {
        viewOverdueBtn.addEventListener('click', viewOverdueTransactions);
    }
    
    // === EDIT FUNCTIONALITY ===
    
    // Edit Book buttons
    const editBookButtons = document.querySelectorAll('.edit-book-btn');
    editBookButtons.forEach(button => {
        button.addEventListener('click', function() {
            const bookId = this.getAttribute('data-book-id');
            loadBookData(bookId);
        });
    });
    
    // Edit Member buttons
    const editMemberButtons = document.querySelectorAll('.edit-member-btn');
    editMemberButtons.forEach(button => {
        button.addEventListener('click', function() {
            const memberId = this.getAttribute('data-member-id');
            loadMemberData(memberId);
        });
    });
    
    // Update available copies when total copies changes
    const totalCopiesInput = document.getElementById('edit_total_copies');
    if (totalCopiesInput) {
        totalCopiesInput.addEventListener('change', updateAvailableCopies);
    }
});

function performSearch() {
    const searchTerm = document.getElementById('searchInput').value;
    if (searchTerm.trim() === '') {
        alert('Please enter a search term');
        return;
    }
    
    fetch(`/books/search?q=${encodeURIComponent(searchTerm)}`)
        .then(response => response.json())
        .then(books => {
            alert(`Found ${books.length} books matching "${searchTerm}"`);
        })
        .catch(error => {
            console.error('Search error:', error);
            alert('Error performing search');
        });
}

function returnBook(transactionId) {
    if (!confirm('Are you sure you want to mark this book as returned?')) {
        return;
    }
    
    fetch(`/transactions/return/${transactionId}`)
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            if (data.success) {
                location.reload();
            }
        })
        .catch(error => {
            console.error('Return error:', error);
            alert('Error returning book');
        });
}

function issueBook() {
    const form = document.getElementById('issueBookForm');
    const formData = new FormData(form);
    
    fetch('/transactions/issue', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (data.success) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('issueBookModal'));
            modal.hide();
            location.reload();
        }
    })
    .catch(error => {
        console.error('Issue error:', error);
        alert('Error issuing book');
    });
}

function viewOverdueTransactions() {
    fetch('/transactions/overdue')
        .then(response => response.json())
        .then(transactions => {
            if (transactions.length === 0) {
                alert('No overdue transactions found');
            } else {
                let message = `Found ${transactions.length} overdue transactions:\n\n`;
                transactions.forEach(trans => {
                    message += `• ${trans.book_title} - Due: ${trans.due_date} (${trans.days_overdue} days overdue)\n`;
                });
                alert(message);
            }
        })
        .catch(error => {
            console.error('Overdue error:', error);
            alert('Error fetching overdue transactions');
        });
}

// === EDIT FUNCTIONS ===

function loadBookData(bookId) {
    fetch(`/books/${bookId}/json`)
        .then(response => response.json())
        .then(book => {
            // Fill the edit form with book data
            document.getElementById('edit_book_id').value = book.id;
            document.getElementById('edit_title').value = book.title;
            document.getElementById('edit_author').value = book.author;
            document.getElementById('edit_isbn').value = book.isbn;
            document.getElementById('edit_publisher').value = book.publisher || '';
            document.getElementById('edit_publication_year').value = book.publication_year || '';
            document.getElementById('edit_category').value = book.category || '';
            document.getElementById('edit_total_copies').value = book.total_copies;
            document.getElementById('edit_available_copies').value = book.available_copies;
            
            // Store original total copies for calculation
            document.getElementById('edit_total_copies').setAttribute('data-original-total', book.total_copies);
            
            // Update form action
            document.getElementById('editBookForm').action = `/books/update/${book.id}`;
        })
        .catch(error => {
            console.error('Error loading book data:', error);
            alert('Error loading book data');
        });
}

function loadMemberData(memberId) {
    fetch(`/members/${memberId}/json`)
        .then(response => response.json())
        .then(member => {
            // Fill the edit form with member data
            document.getElementById('edit_member_id').value = member.id;
            document.getElementById('edit_name').value = member.name;
            document.getElementById('edit_email').value = member.email;
            document.getElementById('edit_phone').value = member.phone || '';
            document.getElementById('edit_status').value = member.status;
            document.getElementById('edit_membership_date').value = member.membership_date;
            
            // Update form action
            document.getElementById('editMemberForm').action = `/members/update/${member.id}`;
        })
        .catch(error => {
            console.error('Error loading member data:', error);
            alert('Error loading member data');
        });
}

function updateAvailableCopies() {
    const totalCopies = parseInt(document.getElementById('edit_total_copies').value) || 0;
    const currentAvailable = parseInt(document.getElementById('edit_available_copies').value) || 0;
    const currentTotal = parseInt(document.getElementById('edit_total_copies').getAttribute('data-original-total')) || totalCopies;
    
    if (currentTotal !== totalCopies) {
        const difference = totalCopies - currentTotal;
        const newAvailable = Math.max(0, currentAvailable + difference);
        document.getElementById('edit_available_copies').value = newAvailable;
    }
}