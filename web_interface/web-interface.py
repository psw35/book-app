from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from datetime import datetime


app = Flask(__name__)

API_GATEWAY_URL = "http://localhost:5000"

@app.route('/')
def index():
   return render_template('index.html')

@app.route("/books/<book_id>")
def book_details(book_id):
   response = requests.get(f"{API_GATEWAY_URL}/books/{book_id}")
   return response.json()

@app.route("/books/<book_id>/reviews", methods=["GET", "POST"])
def book_reviews(book_id):
   if request.method == "POST":
      review_data = request.form.to_dict()
      requests.post(f"{API_GATEWAY_URL}/books/{book_id}/reviews", json=review_data)
      return redirect(f"/books/{book_id}/reviews")
   
   response = requests.get(f"{API_GATEWAY_URL}/books/{book_id}/reviews")
   return response.json()

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=3000, debug=True)
