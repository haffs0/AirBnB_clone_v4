#!/usr/bin/python3
"""
 view for places objects that handles all default RESTFul API actions
"""
from api.v1.views import app_views
from flask import jsonify, request, abort, Flask
from models import storage
from models.place import Place
from models.user import User
from models.city import City
from os import getenv


@app_views.route(
        '/cities/<string:city_id>/places',
        methods=['GET', 'POST'],
        strict_slashes=False)
def place(city_id):
    """users route"""
    city = storage.get('City', city_id)
    if city is None:
        abort(404)
    if request.method == 'GET':
        return jsonify(
                [obj.to_dict() for obj in city.places])
    if request.method == 'POST':
        body = request.get_json()
        if body is None or type(body) != dict:
            return jsonify({'error': 'Not a JSON'}), 400
        new_user_id = body.get('user_id')
        if new_user_id is None:
            return jsonify({'error': 'Missing user_id'}), 400
        user = storage.get('User', new_user_id)
        if user is None:
            abort(404)
        new_name = body.get('name')
        if new_name is None:
            return jsonify({'error': 'Missing name'}), 400
        new_place = Place(city_id=city_id, **body)
        new_place.save()
    return jsonify(new_place.to_dict()), 201


@app_views.route(
        '/places/<string:place_id>',
        methods=['GET', 'DELETE', 'PUT'],
        strict_slashes=False)
def places_with_id(place_id):
    """handle places object with parameter state_id"""
    place = storage.get("Place", place_id)
    if place is None:
        abort(404)
    if request.method == 'GET':
        return jsonify(place.to_dict())
    if request.method == 'DELETE':
        storage.delete(place)
        storage.save()
        return jsonify({}), 200
    if request.method == 'PUT':
        put_data = request.get_json()
        if put_data is None or type(put_data) != dict:
            return jsonify({'error': 'Not a JSON'}), 400
        to_ignore = ['id', 'user_id', 'city_id' 'created_at', 'updated_at']
        place.update(to_ignore, **put_data)
        return jsonify(place.to_dict()), 200


@app_views.route(
    '/places_search',
    methods=['POST'],
    strict_slashes=False)
def places_search():
    """return place objects depending on json body of req"""
    post_data = request.get_json()
    places_search = []
    if post_data is None or type(post_data) != dict:
        return jsonify({'error': 'Not a JSON'}), 400
    places = storage.all('Place').values()
    if len(post_data) == 0:
        return jsonify([obj.to_dict() for obj in places])
    state_ids = post_data.get('states', [])
    city_ids = post_data.get('cities', [])
    amenity_ids = post_data.get('amenities', [])
    if len(state_ids) == 0 and len(city_ids) == 0 and len(amenity_ids) == 0:
        return jsonify([obj.to_dict() for obj in places])
    for ids in city_ids:
        city = storage.get('City', ids)
        if city is not None:
            for p in city.places and p.to_dict() not in places_search:
                places_search.append(p.to_dict())
    for ids in state_ids:
        state = storage.get('State', ids)
        if state is not None:
            for city in state.cities:
                if city.id not in city_ids:
                    for place in city.places:
                        if place.to_dict() not in places_search:
                            places_search.append(place.to_dict())
    for place in places:
        if len(amenity_ids) == 0:
            break
        all_match = True
        if getenv('HBNB_TYPE_STORAGE') != 'db':
            for ids in amenity_ids:
                if ids not in place.amenity_ids:
                    all_match = False
                    break
        else:
            for ids in amenity_ids:
                cur_amenity = storage.get('Amenity', ids)
                if cur_amenity is None or cur_amenity not in place.amenities:
                    all_match = False
                    break
        if all_match is True and place.to_dict() not in places_search:
            places_search.append(place.to_dict())
    return jsonify(places_search)
