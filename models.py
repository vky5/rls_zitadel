from sqlmodel import SQLModel, Field, Relationship
import uuid
from typing import List, Optional

class Tenant(SQLModel, table=True):
    __tablename__ = "tenants"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    
    users: List["User"] = Relationship(back_populates="tenant")
    projects: List["Project"] = Relationship(back_populates="tenant")
    
class User(SQLModel, table=True):
    __tablename__ = "users"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    tenant_id: str = Field(foreign_key="tenants.id")
    
    tenant: Optional[Tenant] = Relationship(back_populates="users")
    
class Project(SQLModel, table = True):
    __tablename__ = "projects"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    tenant_id: str
    
    tenant_id: str = Field(foreign_key="tenants.id")
    
    tenant: Optional[Tenant] = Relationship(back_populates="projects")
    
