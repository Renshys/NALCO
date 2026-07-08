from database import db

print("Connected Database:", db.name)
print("Collections:", db.list_collection_names())