#!/usr/bin/python3
"""
 view for cities objects that handles all default RESTFul API actions
"""
from api.v1.views import app_views
from flask import jsonify, request, abort, Flask
from models import storage
from models.state import State
from models.city import City


@app_views.route(
        '/states/<string:state_id>/cities',
        methods=['GET', 'POST'],
        strict_slashes=False)
def state_cities(state_id):
    """states route"""
    my_state = storage.get("State", state_id)
    if my_state is None:
        abort(404)
    if request.method == 'GET':
        return jsonify(
                [obj.to_dict() for obj in my_state.cities])
    if request.method == 'POST':
        body = request.get_json()
        if body is None or type(body) != dict:
            return jsonify({'error': 'Not a JSON'}), 400
        new_name = body.get('name')
        if new_name is None:
            return jsonify({'error': 'Missing name'}), 400
        new_state_city = City(state_id=state_id, **body)
        new_state_city.save()
    return jsonify(new_state_city.to_dict()), 201


@app_views.route(
        '/cities/<string:city_id>',
        methods=['GET', 'DELETE', 'PUT'],
        strict_slashes=False)
def city_with_id(city_id):
    """handle cities object with parameter state_id"""
    city = storage.get("City", city_id)
    if city is None:
        abort(404)
    if request.method == 'GET':
        return jsonify(city.to_dict())
    if request.method == 'DELETE':
        storage.delete(city)
        storage.save()
        return jsonify({}), 200
    if request.method == 'PUT':
        put_data = request.get_json()
        if put_data is None or type(put_data) != dict:
            return jsonify({'error': 'Not a JSON'}), 400
        to_ignore = ['id', 'created_at', 'updated_at']
        city.update(to_ignore, **put_data)
        return jsonify(city.to_dict()), 200
