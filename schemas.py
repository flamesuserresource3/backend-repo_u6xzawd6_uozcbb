"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import Optional, List

# -----------------------------
# Portfolio/CV Schemas
# -----------------------------

class ExperienceItem(BaseModel):
    role: str
    company: str
    start_date: str
    end_date: Optional[str] = None
    description: Optional[str] = None

class EducationItem(BaseModel):
    school: str
    degree: str
    start_year: Optional[str] = None
    end_year: Optional[str] = None

class Cv(BaseModel):
    """
    Personal CV schema
    Collection name: "cv"
    """
    name: str = Field(..., description="Full name")
    title: str = Field(..., description="Professional title")
    summary: Optional[str] = Field(None, description="Short professional summary")
    location: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience: List[ExperienceItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    website: Optional[HttpUrl] = None
    avatar_url: Optional[HttpUrl] = None

class Project(BaseModel):
    """
    Portfolio projects schema
    Collection name: "project"
    """
    title: str
    description: Optional[str] = None
    tech_stack: List[str] = Field(default_factory=list)
    url: Optional[HttpUrl] = None
    repo_url: Optional[HttpUrl] = None
    image_url: Optional[HttpUrl] = None
    featured: bool = False

# You may keep or remove example schemas below depending on your app's needs.

class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")
