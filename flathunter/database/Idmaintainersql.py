import datetime
import json
import threading
from sqlalchemy import create_engine, Column, Integer, TIMESTAMP, JSON, String, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from flathunter.database.models import Housing  # Import your Housing model here
from flathunter.database.models import Base
from flathunter.database.models import User
from flathunter.database.models import Execution
from flathunter.database.models import Processed


class IdMaintainerSQL:
    """Postgres back-end for the database"""

    def __init__(self, db):
        self.threadlocal = threading.local()
        self.db_singleton = db
        Base.metadata.create_all(bind=db.engine)


    def get_session(self) -> Session:
        """Retrieve a thread-local session."""
        if not hasattr(self.threadlocal, 'session'):
            self.threadlocal.session = self.db_singleton.SessionLocal()
        return self.threadlocal.session

    def is_processed(self, expose_id: int) -> bool:
        """Check if an expose has already been processed."""
        session = self.get_session()
        return session.query(Processed).filter_by(id=expose_id).first() is not None

    def mark_processed(self, expose_id: int):
        """Mark an expose as processed in the database."""
        session = self.get_session()
        session.add(Processed(id=expose_id))
        session.commit()

    def save_expose(self, expose: dict):
        """Save an expose to the database."""
        session = self.get_session()
        l = True if expose.get('lift') == 'True' else False
        new_expose = Housing(
            id=expose['id'],
            created_at=datetime.datetime.now(),
            crawler=expose.get('crawler'),
            json_data=expose,
            image=expose.get('image'),
            url=expose.get('url'),
            title=expose.get('title'),
            price=expose.get('price'),
            size=expose.get('size'),
            rooms=expose.get('rooms'),
            address=expose.get('address'),
            lift=l,
            pricebyarea=expose.get('pricebyarea'),
            district=expose.get('district'),
            bathrooms=expose.get('bathrooms'),
            status=expose.get('status'),
            lat=expose.get('lat'),
            long=expose.get('long'),
            location=f"POINT({expose.get('lat')} {expose.get('long')})"
        )
        session.merge(new_expose)  # Insert or update
        session.commit()

    def get_exposes_since(self, min_datetime: datetime.datetime):
        """Retrieve all exposes created since a specific datetime."""
        session = self.get_session()
        exposes = (
            session.query(Housing)
            .filter(Housing.created_at >= min_datetime)
            .order_by(Housing.created_at.desc())
            .all()
        )
        return [expose.json_data for expose in exposes]

    def get_recent_exposes(self, count: int, filter_func=None):
        """Retrieve up to 'count' recent exposes, optionally filtered."""
        session = self.get_session()
        exposes = session.query(Housing).order_by(Housing.created_at.desc()).limit(count).all()
        if filter_func:
            exposes = [expose for expose in exposes if filter_func(expose)]
        return [expose.json_data for expose in exposes]

    def save_settings_for_user(self, user_id: int, settings: dict):
        """Save user settings."""
        session = self.get_session()
        user = session.merge(User(id=user_id, settings=settings))
        session.commit()

    def get_settings_for_user(self, user_id: int):
        """Retrieve settings for a specific user."""
        session = self.get_session()
        user = session.query(User).filter_by(id=user_id).first()
        return user.settings if user else None

    def get_user_settings(self):
        """Retrieve settings for all users."""
        session = self.get_session()
        users = session.query(User).all()
        return [(user.id, user.settings) for user in users]

    def get_last_run_time(self) -> datetime.datetime:
        """Retrieve the timestamp of the last execution."""
        session = self.get_session()
        last_execution = session.query(Execution).order_by(Execution.timestamp.desc()).first()
        return last_execution.timestamp if last_execution else None

    def update_last_run_time(self) -> datetime.datetime:
        """Save the timestamp of the most recent execution."""
        session = self.get_session()
        current_time = datetime.datetime.now()
        session.add(Execution(timestamp=current_time))
        session.commit()
        return current_time
