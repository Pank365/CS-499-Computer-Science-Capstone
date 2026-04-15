from pymongo import MongoClient
from bson.objectid import ObjectId

class AnimalShelter:
    """CRUD operations for Animal collection in MongoDB"""

    def __init__(self, inputUser, inputPass):
        # Connection configuration
        # USER = 'aacuser'
        # PASS = 'SNHU1234'
        HOST = 'localhost'
        PORT = 27017
        DB = 'aac'
        COL = 'animals'

        # Initialize MongoDB connection
        self.client = MongoClient(f'mongodb://{inputUser}:{inputPass}@{HOST}:{PORT}')
        self.database = self.client[DB]
        self.collection = self.database[COL]

    # CREATE
    def create(self, data: dict):
        if data is not None:
            result = self.collection.insert_one(data)
            return str(result.inserted_id)  # Return the new document ID
        else:
            raise Exception("Nothing to save, because data parameter is empty")

    # READ
    def read(self, query: dict):
        if query is not None:
            try:
                return list(self.collection.find(query))
            except Exception:
                return []
        else:
            return []

    # UPDATE
    def update(self, query: dict, new_values: dict):
        if query and new_values:
            result = self.collection.update_many(query, {"$set": new_values})
            return result.modified_count  # Number of documents updated
        else:
            raise Exception("Both query and new_values must be provided")

    # DELETE
    def delete(self, query: dict):
        if query:
            result = self.collection.delete_many(query)
            return result.deleted_count  # Number of documents deleted
        else:
            raise Exception("Query must be provided")