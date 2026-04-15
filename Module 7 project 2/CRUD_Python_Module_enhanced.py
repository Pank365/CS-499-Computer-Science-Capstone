from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError


class AnimalShelter:
    """CRUD operations for the Animal collection in MongoDB.

    This enhanced version adds:
    - clearer validation and error messages
    - flexible read queries with projection, sorting, and limits
    - safe single-document and multi-document update/delete options
    - connection testing and cleanup helpers
    """

    def __init__(
        self,
        inputUser: str,
        inputPass: str,
        host: str = "localhost",
        port: int = 27017,
        db_name: str = "aac",
        collection_name: str = "animals",
    ) -> None:
        if not inputUser or not inputPass:
            raise ValueError("A MongoDB username and password are required.")

        self.host = host
        self.port = port
        self.db_name = db_name
        self.collection_name = collection_name

        try:
            self.client: MongoClient = MongoClient(
                f"mongodb://{inputUser}:{inputPass}@{host}:{port}",
                serverSelectionTimeoutMS=5000,
            )
            self.client.admin.command("ping")
            self.database: Database = self.client[db_name]
            self.collection: Collection = self.database[collection_name]
        except PyMongoError as exc:
            raise ConnectionError(f"Unable to connect to MongoDB: {exc}") from exc

    def create(self, data: Dict[str, Any]) -> str:
        """Insert one document and return its inserted id."""
        if not isinstance(data, dict) or not data:
            raise ValueError("Data must be a non-empty dictionary.")

        try:
            result = self.collection.insert_one(data)
            return str(result.inserted_id)
        except PyMongoError as exc:
            raise RuntimeError(f"Create operation failed: {exc}") from exc

    def create_many(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Insert multiple documents and return their inserted ids."""
        if not isinstance(documents, list) or not documents:
            raise ValueError("Documents must be a non-empty list of dictionaries.")
        if not all(isinstance(document, dict) and document for document in documents):
            raise ValueError("Each document must be a non-empty dictionary.")

        try:
            result = self.collection.insert_many(documents)
            return [str(inserted_id) for inserted_id in result.inserted_ids]
        except PyMongoError as exc:
            raise RuntimeError(f"Bulk create operation failed: {exc}") from exc

    def read(
        self,
        query: Optional[Dict[str, Any]] = None,
        projection: Optional[Dict[str, int]] = None,
        sort: Optional[Sequence[Tuple[str, int]]] = None,
        limit: int = 0,
    ) -> List[Dict[str, Any]]:
        """Read documents that match a query.

        Args:
            query: MongoDB filter. Defaults to {}.
            projection: Fields to include/exclude.
            sort: Sequence like [("age_upon_outcome_in_weeks", 1)].
            limit: Max documents to return. 0 returns all matches.
        """
        if query is None:
            query = {}
        if not isinstance(query, dict):
            raise ValueError("Query must be a dictionary.")
        if projection is not None and not isinstance(projection, dict):
            raise ValueError("Projection must be a dictionary or None.")
        if limit < 0:
            raise ValueError("Limit cannot be negative.")

        try:
            cursor = self.collection.find(query, projection)
            if sort:
                cursor = cursor.sort(list(sort))
            if limit:
                cursor = cursor.limit(limit)
            return list(cursor)
        except PyMongoError as exc:
            raise RuntimeError(f"Read operation failed: {exc}") from exc

    def update(
        self,
        query: Dict[str, Any],
        new_values: Dict[str, Any],
        multiple: bool = True,
    ) -> int:
        """Update one or many documents and return the modified count."""
        if not isinstance(query, dict) or not query:
            raise ValueError("Query must be a non-empty dictionary.")
        if not isinstance(new_values, dict) or not new_values:
            raise ValueError("new_values must be a non-empty dictionary.")

        try:
            if multiple:
                result = self.collection.update_many(query, {"$set": new_values})
            else:
                result = self.collection.update_one(query, {"$set": new_values})
            return result.modified_count
        except PyMongoError as exc:
            raise RuntimeError(f"Update operation failed: {exc}") from exc

    def delete(self, query: Dict[str, Any], multiple: bool = True) -> int:
        """Delete one or many documents and return the deleted count."""
        if not isinstance(query, dict) or not query:
            raise ValueError("Query must be a non-empty dictionary.")

        try:
            if multiple:
                result = self.collection.delete_many(query)
            else:
                result = self.collection.delete_one(query)
            return result.deleted_count
        except PyMongoError as exc:
            raise RuntimeError(f"Delete operation failed: {exc}") from exc

    def count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """Return the number of matching documents."""
        if query is None:
            query = {}
        if not isinstance(query, dict):
            raise ValueError("Query must be a dictionary.")

        try:
            return self.collection.count_documents(query)
        except PyMongoError as exc:
            raise RuntimeError(f"Count operation failed: {exc}") from exc

    def close(self) -> None:
        """Close the MongoDB connection."""
        self.client.close()
