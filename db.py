from sqlmodel import create_engine, SQLModel
import os

# Database connection URL (adjust your credentials)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://vky5:passwd@127.0.0.1:5432/introspectcore_zitadel_poc"
)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)




def init_db():
    from models import Tenant, User, Project
    SQLModel.metadata.create_all(engine) # creates only missing table doesnt alter existing ones, drop columns renames etc