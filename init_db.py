from main import app, db
from models import Category, Jobs

with app.app_context():
    db.create_all()
    if not Category.query.first():
        initial_categories = [
            Category(name="Engineering"),
            Category(name="Science"),
            Category(name="Management"),
            Category(name="Support")
        ]
        for category in initial_categories:
            db.session.add(category)
        db.session.commit()
        print("Initial categories added to the database.")
    else:
        print("Categories already exist in the database.")

    if not Jobs.query.first():
        initial_jobs = [
            Jobs(job_title="Develop new AI model", team_leader_id=1, work_size=40, collaborators="2,3",
                 is_finished=False),
            Jobs(job_title="Write research paper", team_leader_id=2, work_size=20, collaborators="1,4",
                 is_finished=True),
            Jobs(job_title="Organize team meeting", team_leader_id=3, work_size=5, collaborators="1,2,3,4",
                 is_finished=False)
        ]
        for job in initial_jobs:
            db.session.add(job)
        db.session.commit()
        print("Initial jobs added to the database.")
    else:
        print("Jobs already exist in the database.")

    if not db.session.execute(db.text("SELECT * FROM job_category")).fetchone():
        jobs = Jobs.query.all()
        categories = Category.query.all()
        initial_job_categories = [
            {"job_id": jobs[0].id, "category_id": categories[0].id},
            {"job_id": jobs[0].id, "category_id": categories[1].id},
            {"job_id": jobs[1].id, "category_id": categories[1].id},
            {"job_id": jobs[2].id, "category_id": categories[2].id},
            {"job_id": jobs[2].id, "category_id": categories[3].id}
        ]
        for relation in initial_job_categories:
            db.session.execute(
                db.text("INSERT INTO job_category (job_id, category_id) VALUES (:job_id, :category_id)"),
                {"job_id": relation["job_id"], "category_id": relation["category_id"]}
            )
        db.session.commit()
        print("Initial job-category relationships added to the database.")
    else:
        print("Job-category relationships already exist in the database.")

    print("Database setup completed.")
