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
from os import environ


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
        to_ignore = ['id', 'user_id', 'city_id'
                'created_at', 'updated_at']
        place.update(to_ignore, **put_data)
        return jsonify(place.to_dict()), 200


@app_views.route(
    '/places_search',
    methods=['POST'],
    strict_slashes=False)
def places_search():
    """return place objects depending on json body of req"""
    all_places = [p for p in storage.all('Place').values()]
    req_json = request.get_json()
    if req_json is None:
        abort(400, 'Not a JSON')
    states = req_json.get('states')
    if states and len(states) > 0:
        all_cities = storage.all('City')
        state_cities = set([city.id for city in all_cities.values()
                            if city.state_id in states])
    else:
        state_cities = set()
    cities = req_json.get('cities')
    if cities and len(cities) > 0:
        cities = set([
            c_id for c_id in cities if storage.get('City', c_id)])
        state_cities = state_cities.union(cities)
    amenities = req_json.get('amenities')
    if len(state_cities) > 0:
        all_places = [p for p in all_places if p.city_id in state_cities]
    elif amenities is None or len(amenities) == 0:
        result = [place.to_json() for place in all_places]
        return jsonify(result)
    places_amenities = []
    if amenities and len(amenities) > 0:
        amenities = set([
            a_id for a_id in amenities if storage.get('Amenity', a_id)])
        for p in all_places:
            p_amenities = None
            if environ.get('HBNB_TYPE_STORAGE') == 'db' and p.amenities:
                p_amenities = [a.id for a in p.amenities]
            elif len(p.amenities) > 0:
                p_amenities = p.amenities
            if p_amenities and all([a in p_amenities for a in amenities]):
                places_amenities.append(p)
    else:
        places_amenities = all_places
    result = [place.to_json() for place in places_amenities]
    return jsonify(result)
