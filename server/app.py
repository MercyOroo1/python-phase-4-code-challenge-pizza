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
    restaurant = db.session.get(Restaurant, id)
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
    restaurant = db.session.get(Restaurant, id)
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

@app.route('/pizzas/<int:id>', methods = ['GET'])
def get_pizza(id):
    pizza = db.session.get(Pizza, id)
    if not pizza:
        return jsonify({'msg': 'pizza not found'})
    pizza_data = {
        'id': pizza.id,
        'name': pizza.name,
        'ingredients': pizza.ingredients,
        'restaurant_pizzas': [{
            'id': rp.id,
            'price': rp.price,
            'restaurant': {
                'id': rp.restaurant.id,
                'name': rp.restaurant.name,
                'address': rp.restaurant.address
            }
        } for rp in pizza.restaurant_pizza]
    }
    

    return jsonify(pizza_data)
# restaurant_pizza routes
@app.route('/restaurant_pizzas', methods=['POST'])
def assign_restaurant_pizzas():
    data = request.get_json()

    
    
    if not data or "pizza_id" not in data or "restaurant_id" not in data:
        return jsonify({"error": "Validation failed. Missing pizza_id or restaurant_id in request."}), 400
    
  
    pizza_id = int(data["pizza_id"])
    restaurant_id = int(data["restaurant_id"])
    
   
    pizza = db.session.get(Pizza,pizza_id)
    restaurant = db.session.get(Restaurant,restaurant_id)
    
    
    
    if not pizza or not restaurant:
        return jsonify({"error": "Validation failed. Pizza or Restaurant not found."}), 404
    
    if not (1 <= data["price"] <=30 ):
        return jsonify ({"errors": ["validation errors"]}), 400
    
    
    new_rp = RestaurantPizza(
        price=data["price"],
        restaurant_id=restaurant_id,
        pizza_id=pizza_id
    )
    
    db.session.add(new_rp)
    db.session.commit()
    
    
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
  
if __name__ == "__main__":
    app.run(port=5555, debug=True)
