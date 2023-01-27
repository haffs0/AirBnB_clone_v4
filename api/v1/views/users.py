#!/usr/bin/python3
"""
 view for users objects that handles all default RESTFul API actions
"""
from api.v1.views import app_views
from flask import jsonify, request, abort, Flask
from models import storage
from models.user import User


@app_views.route(
        '/users',
        methods=['GET', 'POST'],
        strict_slashes=False)
def users():
    """users route"""
    if request.method == 'GET':
        return jsonify(
                [obj.to_dict() for obj in storage.all('User').values()])
    if request.method == 'POST':
        body = request.get_json()
        if body is None or type(body) != dict:
            return jsonify({'error': 'Not a JSON'}), 400
        new_email = body.get('email')
        if new_email is None:
            return jsonify({'error': 'Missing email'}), 400
        new_password = body.get('password')
        if new_password is None:
            return jsonify({'error': 'Missing password'}), 400
        new_user = User(**body)
        new_user.save()
    return jsonify(new_user.to_dict()), 201


@app_views.route(
        '/users/<string:user_id>',
        methods=['GET', 'DELETE', 'PUT'],
        strict_slashes=False)
def users_with_id(user_id):
    """handle users object with parameter state_id"""
    user = storage.get("User", user_id)
    if user is None:
        abort(404)
    if request.method == 'GET':
        return jsonify(user.to_dict())
    if request.method == 'DELETE':
        storage.delete(user)
        storage.save()
        return jsonify({}), 200
    if request.method == 'PUT':
        put_data = request.get_json()
        if put_data is None or type(put_data) != dict:
            return jsonify({'error': 'Not a JSON'}), 400
        to_ignore = ['id', 'email', 'created_at', 'updated_at']
        user.update(to_ignore, **put_data)
        return jsonify(user.to_dict()), 200
