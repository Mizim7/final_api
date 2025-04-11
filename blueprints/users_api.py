from flask import Blueprint, jsonify, request, abort, render_template
from models import db, User

users_api_blueprint = Blueprint('users_api', __name__)


@users_api_blueprint.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_list = []
    for user in users:
        user_dict = {
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'jobs': [job.id for job in user.jobs]
        }
        users_list.append(user_dict)
    return jsonify({'users': users_list})


@users_api_blueprint.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'error': 'User not found'}), 404

    user_dict = {
        'id': user.id,
        'email': user.email,
        'name': user.name,
        'jobs': [job.id for job in user.jobs]
    }
    return jsonify({'user': user_dict})


@users_api_blueprint.route('/api/users', methods=['POST'])
def add_user():
    data = request.json
    required_fields = ['email', 'password', 'name']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f"Missing required field: {field}"}), 400

    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'error': "Email already exists"}), 400

    new_user = User(
        email=data['email'],
        password=data['password'],
        name=data['name']
    )
    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Database error: {str(e)}"}), 500

    return jsonify({
        'success': True,
        'user': {
            'id': new_user.id,
            'email': new_user.email,
            'name': new_user.name,
            'jobs': []
        }
    }), 201


@users_api_blueprint.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'error': 'User not found'}), 404

    data = request.json
    try:
        if 'email' in data:
            if User.query.filter(User.email == data['email'], User.id != user_id).first():
                return jsonify({'error': "Email already exists"}), 400
            user.email = data['email']
        if 'password' in data:
            user.password = data['password']
        if 'name' in data:
            user.name = data['name']
    except (ValueError, TypeError):
        return jsonify({'error': "Invalid data type for one or more fields"}), 400

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Database error: {str(e)}"}), 500
    return jsonify({
        'success': True,
        'message': 'User updated successfully',
        'user': {
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'jobs': [job.id for job in user.jobs]
        }
    }), 200


@users_api_blueprint.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    try:
        db.session.delete(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Database error: {str(e)}"}), 500

    return jsonify({'success': True, 'message': 'User deleted successfully'}), 200


@users_api_blueprint.route('/users_show/<int:user_id>', methods=['GET'])
def show_user_hometown(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'error': 'User not found'}), 404

    user_dict = {
        'id': user.id,
        'name': user.name,
        'city_from': user.city_from
    }

    return render_template('user_hometown.html', user=user_dict)