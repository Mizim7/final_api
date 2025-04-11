from flask_restful import Resource, reqparse
from models import db, User

parser = reqparse.RequestParser()
parser.add_argument('email', type=str, required=True, help="Email cannot be blank!")
parser.add_argument('password', type=str, required=True, help="Password cannot be blank!")
parser.add_argument('name', type=str, required=True, help="Name cannot be blank!")
parser.add_argument('city_from', type=str, required=True, help="City From cannot be blank!")


class UsersListResource(Resource):
    def get(self):
        users = User.query.all()
        users_list = []
        for user in users:
            user_dict = {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'city_from': user.city_from
            }
            users_list.append(user_dict)
        return {'users': users_list}, 200

    def post(self):
        args = parser.parse_args()
        if User.query.filter_by(email=args['email']).first():
            return {'error': 'User with this email already exists'}, 400

        new_user = User(
            email=args['email'],
            password=args['password'],
            name=args['name'],
            city_from=args['city_from']
        )

        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'error': f"Database error: {str(e)}"}, 500
        return {
            'success': True,
            'user': {
                'id': new_user.id,
                'email': new_user.email,
                'name': new_user.name,
                'city_from': new_user.city_from
            }
        }, 201


class UsersResource(Resource):
    def get(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        user_dict = {
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'city_from': user.city_from
        }
        return {'user': user_dict}, 200

    def put(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        args = parser.parse_args()
        try:
            if args['email']:
                if User.query.filter(User.email == args['email'], User.id != user_id).first():
                    return {'error': "Email already exists"}, 400
                user.email = args['email']
            if args['password']:
                user.password = args['password']
            if args['name']:
                user.name = args['name']
            if args['city_from']:
                user.city_from = args['city_from']
        except (ValueError, TypeError):
            return {'error': "Invalid data type for one or more fields"}, 400
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'error': f"Database error: {str(e)}"}, 500
        return {
            'success': True,
            'message': 'User updated successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'city_from': user.city_from
            }
        }, 200

    def delete(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        try:
            db.session.delete(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'error': f"Database error: {str(e)}"}, 500
        return {'success': True, 'message': 'User deleted successfully'}, 200
