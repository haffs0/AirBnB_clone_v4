#!/usr/bin/python3
"""
 view for review objects that handles all default RESTFul API actions
"""
from api.v1.views import app_views
from flask import jsonify, request, abort, Flask
from models import storage
from models.place import Place
from models.user import User
from models.review import Review


@app_views.route(
        '/places/<string:place_id>/reviews',
        methods=['GET', 'POST'],
        strict_slashes=False)
def review(place_id):
    """users route"""
    place = storage.get('Place', place_id)
    if place is None:
        abort(404)
    if request.method == 'GET':
        return jsonify(
                [obj.to_dict() for obj in place.reviews])
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
        new_text = body.get('text')
        if new_text is None:
            return jsonify({'error': 'Missing text'}), 400
        new_review = Review(place_id=place_id, **body)
        new_review.save()
    return jsonify(new_review.to_dict()), 201


@app_views.route(
        '/reviews/<string:review_id>',
        methods=['GET', 'DELETE', 'PUT'],
        strict_slashes=False)
def reviews_with_id(review_id):
    """handle reviews object with parameter state_id"""
    review = storage.get("Review", review_id)
    if review is None:
        abort(404)
    if request.method == 'GET':
        return jsonify(review.to_dict())
    if request.method == 'DELETE':
        storage.delete(review)
        storage.save()
        return jsonify({}), 200
    if request.method == 'PUT':
        put_data = request.get_json()
        if put_data is None or type(put_data) != dict:
            return jsonify({'error': 'Not a JSON'}), 400
        to_ignore = ['id', 'user_id', 'place_id' 'created_at', 'updated_at']
        review.update(to_ignore, **put_data)
        return jsonify(review.to_dict()), 200
