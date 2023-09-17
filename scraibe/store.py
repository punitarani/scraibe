"""
scraibe/store.py

Lantern wrapper
"""

import os

from sqlalchemy import create_engine, Column, Integer, String, ARRAY, Float, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


VECTOR_STORE_URL = os.getenv("VECTOR_STORE_URL")

engine = create_engine(VECTOR_STORE_URL)
Session = sessionmaker(bind=engine)
session = Session()


class Vector(Base):
    __tablename__ = "vectors"

    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)
    embedding = Column(ARRAY(Float))


class VectorStore:
    def __init__(self, session):
        self.session = session

    def create_table(self):
        Base.metadata.create_all(engine)

    def insert_vector(self, text, embedding):
        vector = Vector(text=text, embedding=embedding)
        self.session.add(vector)
        self.session.commit()

    def upsert_vector(self, vector_id, text, embedding):
        vector = self.session.query(Vector).filter_by(id=vector_id).first()
        if vector:
            vector.text = text
            vector.embedding = embedding
        else:
            new_vector = Vector(id=vector_id, text=text, embedding=embedding)
            self.session.add(new_vector)
        self.session.commit()

    def update_embedding(self, vector_id, embedding):
        vector = self.session.query(Vector).filter_by(id=vector_id).first()
        if vector:
            vector.embedding = embedding
            self.session.commit()

    def delete_vector(self, vector_id):
        vector = self.session.query(Vector).filter_by(id=vector_id).first()
        if vector:
            self.session.delete(vector)
            self.session.commit()

    def select_nearest(self, embedding, limit=1, filter=None):
        query = self.session.query(Vector.text).order_by(
            func.abs(func.array_distance(Vector.embedding, embedding))
        )
        if filter:
            query = query.filter(filter)
        return query.limit(limit).all()
