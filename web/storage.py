from datetime import datetime
from sqlalchemy import Column, Integer, JSON, String, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from RHTypes.RHClassTypes import Classes
from RHTypes.RHFormatTypes import Formats
from RHTypes.RHHeatTypes import Heats
from RHTypes.RHPilotTypes import Pilots
from RHTypes.RHRaceStatusTypes import RaceStatus
from RHTypes.RHResultTypes import Results
from RHTypes.RHFrequencyTypes import Frequencies
from typing import Generic, TypeVar, Type
import os

T = TypeVar("T")
Base = declarative_base()
db_path = os.getenv("DATABASE_URL", "sqlite:///data.db")  # fallback default
engine = create_engine(db_path)
session_maker = sessionmaker(bind=engine)
session = session_maker()

# Repository methods
def init_db():
    Base.metadata.create_all(bind=engine)

class RHDataTable(Base):
    __tablename__ = "rhdata"

    id = Column(Integer, primary_key=True)
    entry_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class RHDataRepository(Generic[T]):
    stored_type: Type[T]
    typename: str

    def _deserialize(self, payload: dict) -> T:
        return self.stored_type(**payload)

    def store_new_entry(self, value: dict):
        entry = RHDataTable(
                entry_type=self.typename,
                payload = value
            )
        session.add(entry)
        session.commit()

    def get_latest_entry(self) -> T | None:
        entry = (
            session.query(RHDataTable)
            .filter(RHDataTable.entry_type == self.typename)
            .order_by(RHDataTable.timestamp.desc())
            .first()
        )
        if entry is None:
            return None

        return self._deserialize(entry.payload)


# Model classes
class RHClassesRepository(RHDataRepository[Classes]):
    typename = "class_data"
    stored_type = Classes

class RHHeatsRepository(RHDataRepository[Heats]):
    typename = "heat_data"
    stored_type = Heats

class RHPilotsRepository(RHDataRepository[Pilots]):
    typename = "pilot_data"
    stored_type = Pilots

class RHRaceStatusRepository(RHDataRepository[RaceStatus]):
    typename = "race_status"
    stored_type = RaceStatus

class RHResultsRepository(RHDataRepository[Results]):
    typename = "result_data"
    stored_type = Results

class RHFrequencyRepository(RHDataRepository[Frequencies]):
    typename = "frequency_data"
    stored_type = Frequencies

class RHFormatsRepository(RHDataRepository[Formats]):
    typename = "format_data"
    stored_type = Formats
