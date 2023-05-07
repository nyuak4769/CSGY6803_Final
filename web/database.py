from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import json

engine = create_engine('mysql://root:welcome1@127.0.0.1:33061/vault',
                       connect_args={})
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))


Model = declarative_base(name='Model')
Model.query = db_session.query_property()


class Event(Model):
    __tablename__ = 'Event'
    Id = Column(String(128), primary_key=True)
    EventCode = Column(String(128))
    Timestamp = Column(DateTime)
    SecretId = Column(String(127))

    def __init__(self, Id, EventCode, Timestamp, SecretId):
        self.Id = Id
        self.EventCode = EventCode
        self.Timestamp = Timestamp
        self.SecretId = SecretId

    def toDict(self):
        return dict(Id=str(self.Id), EventCode=str(self.EventCode), Timestamp=str(self.Timestamp),
                               SecretId=str(self.SecretId))

    def __str__(self):
        return str(self.toDict())