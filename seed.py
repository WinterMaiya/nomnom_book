from app import db

db.drop_all()
print("Dropping database")
db.create_all()
print("Database created")
print(db)
