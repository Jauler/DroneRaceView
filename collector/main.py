import argparse
import logging
import socketio
import time
import threading
import os
from sqlalchemy import create_engine, Column, Integer, DateTime, JSON, String
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# --- Logging setup ---
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger("SocketIOListener")

# --- SQLAlchemy setup ---
Base = declarative_base()
db_path = os.getenv("DATABASE_URL", "sqlite:///data.db")  # fallback default
engine = create_engine(db_path)
session_maker = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

class RHDataTable(Base):
    __tablename__ = "rhdata"

    id = Column(Integer, primary_key=True)
    entry_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


ignored_events = None
store_events = None
store_max_event_count = None

# --- Socket.IO Client setup ---
sio = socketio.Client(reconnection=False)  # We will handle reconnection manually

def save_event(event_name, data):
    try:
        global ignored_events
        if not data:
            return
        if ignored_events and event_name in ignored_events:
            return
        if store_events and event_name not in store_events:
            return
        session = session_maker()
        entry = RHDataTable(entry_type=event_name, payload=data)
        session.add(entry)

        if store_max_event_count is not None:
            # Count events in this category
            events = (
                session.query(RHDataTable)
                .filter_by(entry_type=event_name)
                .order_by(RHDataTable.timestamp.desc())
                .all()
            )

            for e in events[store_max_event_count:]:
                session.delete(e)

        session.commit()
        session.close()
        logger.debug(f"Saved event '{event_name}' to database.")
    except Exception:
        logger.exception("Fatal error while saving event — terminating app")
        os._exit(1)  # 🚨 Exit immediately on DB error

# Catch-all event handler
@sio.on("*")
def catch_all(event, data=None):
    save_event(event, data)

@sio.event
def connect():
    logger.info("Connected to Socket.IO server")

@sio.event
def disconnect():
    logger.warning("Disconnected from Socket.IO server")

def periodic_load_all():
    while True:
        if sio.connected:
            logger.info("Emitting 'load_all'")
            load_data_types = [
                        "node_data",
                        "frequency_data",
                        "pilot_data",
                        "heat_data",
                        "class_data",
                        "result_data",
                        "race_status",
                    ]

            if store_events is not None:
                load_data_types = store_events

            data = {"load_types": load_data_types}
            sio.emit("load_data", data=data)
        else:
            logger.warning("Skipping 'load_all' emit because client is disconnected")

        time.sleep(300)

def run_socketio_client(url, username, password):
    while True:
        try:
            logger.info(f"Connecting to {url} with user '{username}'")
            sio.connect(
                url,
                auth={"username": username, "password": password},
                transports=["websocket"]
            )
            # Start periodic message sender
            load_all_thread = threading.Thread(target=periodic_load_all, daemon=True)
            load_all_thread.start()
            sio.wait()
        except Exception as e:
            logger.exception(f"Socket.IO connection error, will retry in 60s: {e}")
            time.sleep(60)

# --- Argparse CLI ---
def main():
    parser = argparse.ArgumentParser(description="Socket.IO client with DB logging.")
    parser.add_argument("--url", required=True, help="Socket.IO server URL")
    parser.add_argument("--username", required=True, help="Username for authentication")
    parser.add_argument("--password", required=True, help="Password for authentication")
    parser.add_argument("--ignore-events", help="Comma-separated list of events to ignore", default=None)
    parser.add_argument("--store-events", help="Comma-separated list of events to store. Will only store these events if specified", default=None)
    parser.add_argument("--store-max-events", help="Maximum number of events to store in DB", type=int)

    args = parser.parse_args()

    if args.ignore_events:
        global ignored_events
        ignored_events = set([e.strip() for e in args.ignore_events.split(",") if e.strip()])

    if args.store_events:
        global store_events
        store_events = set([e.strip() for e in args.store_events.split(",") if e.strip()])

    if args.store_max_events:
        global store_max_event_count
        store_max_event_count = args.store_max_events

    run_socketio_client(args.url, args.username, args.password)

if __name__ == "__main__":
    main()



