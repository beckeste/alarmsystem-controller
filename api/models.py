from sqlalchemy import create_engine, Column, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///sensors.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Sensor(Base):
    __tablename__ = 'sensors'
    mac_address = Column(String, primary_key=True)  # Zeichenkette als Primärschlüssel
    name = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String)
    buzzer = Column(Boolean, default=False)
    door_sensor = Column(Boolean, default=False)
    shutter_sensor = Column(Boolean, default=False)
    motion_sensor = Column(Boolean, default=False)
    siren = Column(Boolean, default=False)
    
    # Zustände der Sensoren
    door_open = Column(Boolean, default=False)
    shutter_open = Column(Boolean, default=False)
    motion_detected = Column(Boolean, default=False)
    siren_on = Column(Boolean, default=False)
    buzzer_on = Column(Boolean, default=False)
    armed = Column(Boolean, default=False)

Base.metadata.create_all(engine)