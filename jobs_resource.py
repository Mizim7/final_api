from flask_restful import Resource, reqparse
from models import db, Jobs, Category
from sqlalchemy.orm import joinedload

parser = reqparse.RequestParser()
parser.add_argument('job_title', type=str, required=True, help="Job title cannot be blank!")
parser.add_argument('team_leader_id', type=int, required=True, help="Team leader ID cannot be blank!")
parser.add_argument('work_size', type=int, required=True, help="Work size cannot be blank!")
parser.add_argument('collaborators', type=str, required=False)
parser.add_argument('is_finished', type=bool, required=False)
parser.add_argument('category_ids', type=int, action='append', required=False)


class JobsListResource(Resource):
    def get(self):
        try:
            jobs = Jobs.query.options(joinedload(Jobs.categories)).all()
            jobs_list = []
            for job in jobs:
                job_dict = {
                    'id': job.id,
                    'job_title': job.job_title,
                    'team_leader_id': job.team_leader_id,
                    'work_size': job.work_size,
                    'collaborators': job.collaborators,
                    'is_finished': job.is_finished,
                    'categories': [category.name for category in job.categories]
                }
                jobs_list.append(job_dict)
            return {'jobs': jobs_list}, 200
        except Exception as e:
            return {'error': f"Database error: {str(e)}"}, 500

    def post(self):
        args = parser.parse_args()
        if not args['job_title']:
            return {'error': 'Job title cannot be blank!'}, 400
        if not args['team_leader_id']:
            return {'error': 'Team leader ID cannot be blank!'}, 400
        if not args['work_size']:
            return {'error': 'Work size cannot be blank!'}, 400

        new_job = Jobs(
            job_title=args['job_title'],
            team_leader_id=args['team_leader_id'],
            work_size=args['work_size'],
            collaborators=args['collaborators'],
            is_finished=args.get('is_finished', False)
        )

        if args['category_ids']:
            categories = Category.query.filter(Category.id.in_(args['category_ids'])).all()
            if len(categories) != len(args['category_ids']):
                return {'error': 'One or more categories do not exist'}, 400
            new_job.categories.extend(categories)

        try:
            db.session.add(new_job)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'error': f"Database error: {str(e)}"}, 500

        return {
            'success': True,
            'job': {
                'id': new_job.id,
                'job_title': new_job.job_title,
                'team_leader_id': new_job.team_leader_id,
                'work_size': new_job.work_size,
                'collaborators': new_job.collaborators,
                'is_finished': new_job.is_finished,
                'categories': [category.name for category in new_job.categories]
            }
        }, 201


class JobsResource(Resource):
    def get(self, job_id):
        try:
            job = db.session.get(Jobs, job_id)
            if not job:
                return {'error': 'Job not found'}, 404

            job_dict = {
                'id': job.id,
                'job_title': job.job_title,
                'team_leader_id': job.team_leader_id,
                'work_size': job.work_size,
                'collaborators': job.collaborators,
                'is_finished': job.is_finished,
                'categories': [category.name for category in job.categories]
            }
            return {'job': job_dict}, 200
        except Exception as e:
            return {'error': f"Database error: {str(e)}"}, 500

    def put(self, job_id):
        try:
            job = db.session.get(Jobs, job_id)
            if not job:
                return {'error': 'Job not found'}, 404

            args = parser.parse_args()
            if args['job_title']:
                job.job_title = args['job_title']
            if args['team_leader_id']:
                job.team_leader_id = args['team_leader_id']
            if args['work_size']:
                job.work_size = args['work_size']
            if args['collaborators']:
                job.collaborators = args['collaborators']
            if args['is_finished'] is not None:
                job.is_finished = args['is_finished']

            if args['category_ids']:
                categories = Category.query.filter(Category.id.in_(args['category_ids'])).all()
                if len(categories) != len(args['category_ids']):
                    return {'error': 'One or more categories do not exist'}, 400
                job.categories = categories

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'error': f"Database error: {str(e)}"}, 500

        return {
            'success': True,
            'message': 'Job updated successfully',
            'job': {
                'id': job.id,
                'job_title': job.job_title,
                'team_leader_id': job.team_leader_id,
                'work_size': job.work_size,
                'collaborators': job.collaborators,
                'is_finished': job.is_finished,
                'categories': [category.name for category in job.categories]
            }
        }, 200

    def delete(self, job_id):
        try:
            job = db.session.get(Jobs, job_id)
            if not job:
                return {'error': 'Job not found'}, 404

            db.session.delete(job)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'error': f"Database error: {str(e)}"}, 500

        return {'success': True, 'message': 'Job deleted successfully'}, 200
