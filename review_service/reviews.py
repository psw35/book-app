from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import requests


app = Flask(__name__)


BOOK_SERVICE_URL = 'http://book-service:5001/api/books'


def get_db_connection():
   conn = sqlite3.connect('reviews.db')
   conn.row_factory = sqlite3.Row
   return conn


def init_db():
   connection = get_db_connection()
   with open('reviews.sql', 'r') as f:
       connection.executescript(f.read())
   connection.commit()
   connection.close()


def verify_book_exists(book_id):
   try:
       response = requests.get(f'{BOOK_SERVICE_URL}/{book_id}')
       return response.status_code == 200
   except requests.RequestException:
       return False


@app.route('/api/reviews/<int:book_id>', methods=['GET'])
def get_reviews(book_id):
   conn = get_db_connection()
   reviews = conn.execute('SELECT * FROM reviews WHERE book_id = ?', (book_id,)).fetchall()
   conn.close()
   return jsonify([dict(review) for review in reviews])


@app.route('/api/reviews', methods=['POST'])
def add_review():
   if not request.json:
       return jsonify({'error': 'No data provided'}), 400
  
   required_fields = ['book_id', 'rating', 'comment', 'reviewer']
   if not all(field in request.json for field in required_fields):
       return jsonify({'error': 'Missing required fields'}), 400
  
   if not verify_book_exists(request.json['book_id']):
       return jsonify({'error': 'Book not found'}), 404
  
   conn = get_db_connection()
   cursor = conn.execute(
       'INSERT INTO reviews (book_id, rating, comment, reviewer, date) VALUES (?, ?, ?, ?, ?)',
       (
           request.json['book_id'],
           request.json['rating'],
           request.json['comment'],
           request.json['reviewer'],
           datetime.now().strftime("%Y-%m-%d")
       )
   )
   review_id = cursor.lastrowid
   conn.commit()
   conn.close()
  
   return jsonify({'id': review_id, 'message': 'Review added successfully'}), 201

# ADD HERE THE REST OF THE FUNCTIONS FOR THE OTHER OPERATIONS:
@app.route('/api/reviews/<int:review_id>', methods=['PUT'])
def update_review(review_id):
    if not request.json:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['book_id', 'rating', 'comment', 'reviewer']
    if not all(field in request.json for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = get_db_connection()
    cursor = conn.execute(
        'UPDATE reviews SET book_id = ?, rating = ?, comment = ?, reviewer = ? WHERE id = ?',
        (request.json['book_id'], request.json['rating'], request.json['comment'], request.json['reviewer'], review_id)
    )
    conn.commit()
    updated_rows = cursor.rowcount
    conn.close()

    if updated_rows == 0:
        return jsonify({'error': 'Review does not exist'}), 404
    
    return jsonify({'id': review_id, 'message': 'Review updated successfully'}), 201

@app.route('/api/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    if not request.json:
       return jsonify({'error': 'No data provided'}), 400
   
    conn = get_db_connection()
    cursor = conn.execute(
        'DELETE FROM reviews WHERE id = ?',
        (review_id,)
    )
    conn.commit()
    deleted_rows = cursor.rowcount
    conn.close()

    if deleted_rows == 0:
        return jsonify({'error': 'Review not found'}), 404

    return jsonify({'id': review_id, 'message': 'Review deleted'})

if __name__ == '__main__':
   init_db()
   app.run(host='0.0.0.0', port=5002)