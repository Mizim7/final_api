from flask import Blueprint, jsonify, request, abort
from models import db, Jobs, Category

jobs_api_blueprint = Blueprint('jobs_api', __name__)


@jobs_api_blueprint.route('/api/jobs', methods=['GET'])
def get_jobs():
    jobs = Jobs.query.all()
    jobs_list = []
    for job in jobs:
        job_dict = {
            'id': job.id,
            'job_title': job.job_title,
            'team_leader_id': job.team_leader_id,
            'work_size': job.work_size,
            'collaborators': job.collaborators,
            'is_finished': job.is_finished,
            'categories': [category.id for category in job.categories]
        }
        jobs_list.append(job_dict)
    return jsonify({'jobs': jobs_list})


@jobs_api_blueprint.route('/api/jobs/<int:job_id>', methods=['GET', 'DELETE'])
def job_handler(job_id):
    job = Jobs.query.get(job_id)
    if job is None:
        return jsonify({'error': 'Job not found'}), 404

    if request.method == 'GET':
        job_dict = {
            'id': job.id,
            'job_title': job.job_title,
            'team_leader_id': job.team_leader_id,
            'work_size': job.work_size,
            'collaborators': job.collaborators,
            'is_finished': job.is_finished,
            'categories': [category.id for category in job.categories]
        }
        return jsonify({'job': job_dict}), 200

    elif request.method == 'DELETE':
        try:
            db.session.delete(job)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f"Database error: {str(e)}"}), 500

        return jsonify({'success': True, 'message': 'Job deleted successfully'}), 200


@jobs_api_blueprint.route('/api/jobs', methods=['POST'])
def add_job():
    data = request.json
    required_fields = ['job_title', 'team_leader_id', 'work_size', 'collaborators']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f"Missing required field: {field}"}), 400

    try:
        team_leader_id = int(data['team_leader_id'])
        work_size = int(data['work_size'])
        is_finished = bool(data.get('is_finished', False))
    except (ValueError, TypeError):
        return jsonify({'error': "Invalid data type for team_leader_id or work_size"}), 400

    categories = []
    if 'categories' in data:
        if not isinstance(data['categories'], list) or not all(isinstance(cat, int) for cat in data['categories']):
            return jsonify({'error': "Invalid category IDs"}), 400

        existing_categories = Category.query.filter(Category.id.in_(data['categories'])).all()
        if len(existing_categories) != len(data['categories']):
            return jsonify({'error': "One or more category IDs do not exist"}), 400
        categories = existing_categories
    new_job = Jobs(
        job_title=data['job_title'],
        team_leader_id=team_leader_id,
        work_size=work_size,
        collaborators=data['collaborators'],
        is_finished=is_finished
    )
    if categories:
        new_job.categories.extend(categories)
    try:
        db.session.add(new_job)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Database error: {str(e)}"}), 500

    return jsonify({
        'success': True,
        'job': {
            'id': new_job.id,
            'job_title': new_job.job_title,
            'team_leader_id': new_job.team_leader_id,
            'work_size': new_job.work_size,
            'collaborators': new_job.collaborators,
            'is_finished': new_job.is_finished,
            'categories': [category.id for category in new_job.categories]
        }
    }), 201


@jobs_api_blueprint.route('/api/jobs/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    job = Jobs.query.get(job_id)
    if job is None:
        return jsonify({'error': 'Job not found'}), 404

    data = request.json
    try:
        if 'job_title' in data:
            job.job_title = data['job_title']
        if 'team_leader_id' in data:
            job.team_leader_id = int(data['team_leader_id'])
        if 'work_size' in data:
            job.work_size = int(data['work_size'])
        if 'collaborators' in data:
            job.collaborators = data['collaborators']
        if 'is_finished' in data:
            job.is_finished = bool(data['is_finished'])
        if 'categories' in data:
            if not isinstance(data['categories'], list) or not all(isinstance(cat, int) for cat in data['categories']):
                return jsonify({'error': "Invalid category IDs"}), 400

            existing_categories = Category.query.filter(Category.id.in_(data['categories'])).all()
            if len(existing_categories) != len(data['categories']):
                return jsonify({'error': "One or more category IDs do not exist"}), 400
            job.categories = existing_categories

    except (ValueError, TypeError):
        return jsonify({'error': "Invalid data type for one or more fields"}), 400

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Database error: {str(e)}"}), 500

    return jsonify({
        'success': True,
        'message': 'Job updated successfully',
        'job': {
            'id': job.id,
            'job_title': job.job_title,
            'team_leader_id': job.team_leader_id,
            'work_size': job.work_size,
            'collaborators': job.collaborators,
            'is_finished': job.is_finished,
            'categories': [category.id for category in job.categories]
        }
    }), 200
