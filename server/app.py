#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response,jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# @app.route("/restaurants")
# def get_restaurants():
#     restaurants = []
#     for restaurant in Restaurant.query.all():
#         restaurant_dict = {
#             "id": restaurant.id,
#             "name": restaurant.name,
#             "address": restaurant.address
#         }
#         restaurants.append(restaurant_dict)
#     return jsonify(restaurants)

# restaurant routes
@app.route('/restaurants', methods = ['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([{
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address
    } for restaurant in restaurants])

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({'error': 'Restaurant not found'}), 404
    

    restaurant_data = {
        'id': restaurant.id,
        'name': restaurant.name,
        'address': restaurant.address,
        'restaurant_pizzas': [
            {
                'id': rp.id,
                'price': rp.price,
                'pizza': {
                    'id': rp.pizza.id,
                    'name': rp.pizza.name,
                    'ingredients': rp.pizza.ingredients
                }
            } for rp in restaurant.restaurant_pizza
        ]
    }
    
    return jsonify(restaurant_data)

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404
    
    db.session.delete(restaurant)
    db.session.commit()
    return jsonify({}), 204

# pizza routes
@app.route('/pizzas', methods = ['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([{
        "id":pizza.id,
        "ingredients":pizza.ingredients,
        "name": pizza.name
    } for pizza in pizzas])

# restaurant_pizza routes
@app.route('/restaurant_pizzas', methods=['POST'])
def assign_restaurant_pizzas():
    data = request.get_json()

    
    
    if not data or "pizza_id" not in data or "restaurant_id" not in data:
        return jsonify({"error": "Validation failed. Missing pizza_id or restaurant_id in request."}), 400
    
    # Ensure pizza_id and restaurant_id are integers
    pizza_id = int(data["pizza_id"])
    restaurant_id = int(data["restaurant_id"])
    
    # Check if Pizza and Restaurant exist
    pizza = Pizza.query.get(pizza_id)
    restaurant = Restaurant.query.get(restaurant_id)
    
    if not pizza or not restaurant:
        return jsonify({"error": "Validation failed. Pizza or Restaurant not found."}), 404
    
    if not (1 <= data["price"] <=30 ):
        return jsonify ({"errors": ["validation errors"]}), 400
    
    # Create new RestaurantPizza entry
    new_rp = RestaurantPizza(
        price=data["price"],
        restaurant_id=restaurant_id,
        pizza_id=pizza_id
    )
    
    db.session.add(new_rp)
    db.session.commit()
    
    # Prepare JSON response
    return jsonify({
        "id": new_rp.id,
        "pizza": {
            "id": pizza.id,
            "name": pizza.name,
            "ingredients": pizza.ingredients
        },
        "pizza_id": new_rp.pizza_id,
        "price": new_rp.price,
        "restaurant": {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address
        },
        "restaurant_id": new_rp.restaurant_id
    }),201
    # restaurant = Restaurant.query.get(restaurant_id)
    # if not restaurant:
    #     return jsonify({'error': 'Restaurant not found'})
    # pizza = Pizza.query.get(pizza_id)
    # if not pizza:
    #     return jsonify({'error': 'Pizza not found'})
    
if __name__ == "__main__":
    app.run(port=5555, debug=True)
