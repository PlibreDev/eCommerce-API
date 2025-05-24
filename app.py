from __future__ import annotations
from flask import Flask, request, jsonify
from sqlalchemy import Integer, String, DateTime, ForeignKey, Column, Table, Float, select
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow 
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from marshmallow import ValidationError
from typing import Optional, List
import os
import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root:pj627129@localhost:3306/ecommerce_api"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Base class for SQLAlchemy
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)
ma = Marshmallow(app)

# OrderProduct association table
class OrderProduct(Base):
    __tablename__ = 'order_product'
    order_id = Column(Integer, ForeignKey('orders.id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)

# User table
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    address: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="user")

# Order table
class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    order_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="orders")
    products: Mapped[List["Product"]] = relationship("Product", secondary=OrderProduct.__table__, back_populates="orders")

# Product table
class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String(200), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    orders: Mapped[List["Order"]] = relationship("Order", secondary=OrderProduct.__table__, back_populates="products")


#Marshmallow Schemas
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True

class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        include_fk = True
        # Include foreign keys in the schema
        load_instance = True

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True

class OrderProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = OrderProduct        
        load_instance = True


# Initialize schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
order_product_schema = OrderProductSchema()
order_products_schema = OrderProductSchema(many=True)


# Implementing the CRUD operations


# User CRUD endpoints
# Create new user
@app.route('/users', methods=['POST'])
def add_user():
    try:
        user_data = user_schema.load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    db.session.add(user_data)  # Add the loaded User instance
    db.session.commit()
    return user_schema.jsonify(user_data), 201

# Get all users
@app.route('/users', methods=['GET'])
def get_users():
    query = select(User)
    users = db.session.execute(query).scalars().all()

    return users_schema.jsonify(users), 200

# Get user by ID
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = db.session.get(User, id)
    return user_schema.jsonify(user), 200

# Update user by ID
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = db.session.get(User, id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    try:
        user_data = user_schema.load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400

    user.name = user_data.name
    user.address = user_data.address
    user.email = user_data.email

    db.session.commit()
    return user_schema.jsonify(user), 200

#Delete user by ID
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = db.session.get(User, id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200


# Product CRUD endpoints
# Retreive all products
@app.route('/products', methods=['GET'])
def get_products():
    query = select(Product)
    products = db.session.execute(query).scalars().all()

    return products_schema.jsonify(products), 200

# Retreive product by ID
@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = db.session.get(Product, id)
    return product_schema.jsonify(product), 200

# Create new product
@app.route('/products', methods=['POST'])    
def add_product():
    try:
        product_data = product_schema.load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.add(product_data) 
    db.session.commit()
    return product_schema.jsonify(product_data), 201

# Update product by ID
@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):        
    product = db.session.get(Product, id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    try:
        product_data = product_schema.load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400

    product.product_name = product_data.product_name
    product.price = product_data.price

    db.session.commit()
    return product_schema.jsonify(product), 200

# Delete product by ID
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = db.session.get(Product, id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'}), 200


# Order CRUD endpoints
# Create new order for a user with order date
@app.route('/orders', methods=['POST'])
def add_order():    
    try:
        order_data = order_schema.load(request.get_json())
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Validate user_id exists
    user = db.session.get(User, order_data.user_id)
    if not user:
        return jsonify({'message': 'User not found for the given user_id'}), 404

    db.session.add(order_data)
    db.session.commit()
    return order_schema.jsonify(order_data), 201

# Add a product to an order (preventing duplicates)
@app.route('/orders/<int:order_id>/add_product/<int:product_id>', methods=['PUT'])
def add_product_to_order(order_id, product_id):
    order = db.session.get(Order, order_id)
    product = db.session.get(Product, product_id)
    if not order or not product:
        return jsonify({'message': 'Order or Product not found'}), 404
    
    # Check for existing entry
    existing = db.session.execute(
        select(OrderProduct).where(
            OrderProduct.order_id == order_id,
            OrderProduct.product_id == product_id
        )
    ).scalar_one_or_none()
    if existing:
        return jsonify({'message': 'Product already in order'}), 400

    new_order_product = OrderProduct(order_id=order_id, product_id=product_id)
    db.session.add(new_order_product)
    db.session.commit()
    return order_product_schema.jsonify(new_order_product), 201

# Remove a product from an order
@app.route('/orders/<int:order_id>/remove_product', methods=['DELETE'])
def remove_product_from_order(order_id):
    product_id = request.args.get('product_id', type=int)
    if not product_id:
        return jsonify({'message': 'product_id is required'}), 400
    
    order_product = db.session.get(OrderProduct, (order_id, product_id))
    if not order_product:
        return jsonify({'message': 'OrderProduct not found'}), 404

    db.session.delete(order_product)
    db.session.commit()
    return jsonify({'message': 'OrderProduct deleted successfully'}), 200

# Get all orders for a user
@app.route('/orders/user/<int:user_id>', methods=['GET'])
def get_orders_for_user(user_id):
    query = select(Order).where(Order.user_id == user_id)
    orders = db.session.execute(query).scalars().all()
    return orders_schema.jsonify(orders), 200

# Get all products in an order
@app.route('/orders/<int:order_id>/products', methods=['GET'])
def get_products_in_order(order_id):
    query = select(Product).join(OrderProduct).where(OrderProduct.order_id == order_id)
    products = db.session.execute(query).scalars().all()

    return products_schema.jsonify(products), 200





if __name__ == "__main__":
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    app.run(debug=True)