from datetime import datetime
from sqlalchemy import Column, Integer, JSON, String, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from RHClassTypes import Classes
from RHHeatTypes import Heats
from RHPilotTypes import Pilots
from RHRaceStatusTypes import RaceStatus
from RHResultTypes import Results
from RHFrequencyTypes import Frequencies
from typing import Generic, TypeVar, Type

T = TypeVar("T")
Base = declarative_base()

engine = create_engine("sqlite:///data.db")
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
