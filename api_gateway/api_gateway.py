from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

SERVICES = {
    'book_service': 'http://book-service:5001/api/books',
    'review_service': 'http://review-service:5002/api/reviews',
}

class APIGateway:
    @staticmethod
    def forward_request(service_name, path):
        """Simple request forwarding"""
        url = f"{SERVICES[service_name]}{path}"
        try:
            response = requests.get(url)
            return response.json()
        except:
            return {'error': 'Service unavailable'}
        
# api gateway routes
@app.route('/books')
def books():
   try:
       response = requests.get('book_service')
       response.raise_for_status()
       books = response.json()
       return render_template('books.html', books=books)
   except requests.RequestException as e:
       flash(f'Error fetching books: {str(e)}')
       return render_template('books.html', books=[])

@app.route('/books/<int:book_id>')
def book_details(book_id):
   try:
       # Get book details
       book_response = requests.get(f'{'book_service'}/{book_id}')
       book_response.raise_for_status()
       book = book_response.json()
      
       # Get book reviews
       reviews_response = requests.get(f'{'review_service'}/{book_id}')
       reviews_response.raise_for_status()
       reviews = reviews_response.json()
      
       return render_template('reviews.html', book=book, reviews=reviews)
   except requests.RequestException as e:
       flash(f'Error fetching data: {str(e)}')
       return redirect(url_for('books'))


@app.route('/books/add', methods=['POST'])
def add_book():
   book_data = {
       'title': request.form['title'],
       'author': request.form['author'],
       'year': int(request.form['year'])
   }
  
   try:
       response = requests.post('book_service', json=book_data)
       response.raise_for_status()
       flash('Book added successfully!')
   except requests.RequestException as e:
       flash(f'Error adding book: {str(e)}')
  
   return redirect(url_for('books'))


@app.route('/reviews/add', methods=['POST'])
def add_review():
   review_data = {
       'book_id': int(request.form['book_id']),
       'rating': int(request.form['rating']),
       'comment': request.form['comment'],
       'reviewer': request.form['reviewer']
   }
  
   try:
       response = requests.post('review_service', json=review_data)
       response.raise_for_status()
       flash('Review added successfully!')
   except requests.RequestException as e:
       flash(f'Error adding review: {str(e)}')
  
   return redirect(url_for('book_details', book_id=review_data['book_id']))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)