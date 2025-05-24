# eCommerce API Documentation

## Introduction

This API provides endpoints for managing users, products, and orders. It uses Flask as the web framework, SQLAlchemy for database operations, and Marshmallow for data serialization and validation.

## What I learned
One of the most important aspects of this project for me was not just generating the code, which was a huge challenge, but understanding how each individual program, dependency, and the API worked together. When I finished writing the API, I had so many errors but, by working through the code to complete a fully functional API I began to understand the bigger picture. Then I realized I still had no idea. 

The Flask development server is the heart of the API's functionality because it ties together MySQL, the Python code, and Postman. In this project, Postman was used for testing but it also serves as a placeholder, in this particular case, in the absence of a front end application that would be responsible for registering users, creating orders, and other more advanced functions. A web app, a shopify store, or a retailer's website would also require adding, or removing products from the order, deleting an order, as well as calculating order totals, matching the user to an order with products as they are added to the order, order cancellation, or order history for a user. Marshmallow made the use of JSON simple, because I wasn't required to handle that data, except during testing when adding a single user, product, or order.

It was very interesting to see the speed at which the API calls were executed even though the data was spread out over multiple relational databases, programs, and interfaces.

## Endpoints

### Users

* `POST /users`: Create a new user
* `GET /users/<int:id>`: Get a user by ID
* `GET /users`: Get all users
* `DELETE /users/<int:id>`: Delete a user

### Products

* `POST /products`: Create a new product
* `GET /products/<int:id>`: Get a product by ID
* `GET /products`: Get all products
* `DELETE /products/<int:id>`: Delete a product

### Orders

* `POST /orders`: Create a new order
* `GET /orders/<int:id>`: Get an order by ID
* `GET /orders/user/<int:user_id>`: Get all orders for a user
* `PUT /orders/<int:order_id>/add_product/<int:product_id>`: Add a product to an order
* `DELETE /orders/<int:order_id>/remove_product`: Remove a product from an order

## Running the Application

## Setup Instructions
## 1. Clone the repository:
git clone [<repo-url>](https://github.com/PlibreDev/eCommerce-API)
cd module-3-project

## 2. Set up a virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows

source venv/bin/activate  # On macOS/Linux

## 3. Install dependencies
pip install -r requirements.txt

### Dependencies

* Flask
* SQLAlchemy
* Flask-Marshmallow
* mysql-connector-python

## 4. Ensure MySQL is running and create the database.
CREATE DATABASE ecommerce_api;

## 5. Update the SQLALCHEMY_DATABASE_URI in app.py with your MySQL root password.

### Notes

This API uses a MySQL database. Make sure you have a MySQL server running and update the database connection settings in `app.py` accordingly.

## 6. Run the app:
python app.py

## 7. Import the Postman Collection to test the endpoints

