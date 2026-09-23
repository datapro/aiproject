from pydantic import BaseModel, EmailStr  # pyright: ignore[reportMissingImports]
from pydantic_settings import BaseSettings, SettingsConfigDict

class UserRegister(BaseModel):
    name: str
    role: str
    email: EmailStr
    password: str

class EssayMarkingCreate(BaseModel):
    student_name: str
    course: str
    exam_title: str
    question: str
    max_score: int
    extracted_text: str  # Store the extracted text
    score: int  # Store the score given by AI
    percentage: float  # Store the percentage score
    grade: str  # Store the grade assigned by AI
    feedback: str  # Store the feedback provided by AI
    strengths: str  # Store the strengths identified by AI
    improvements: str  # Store the areas of improvement identified by AI
    filename: str  # Store the filename of the uploaded answer file

class Settings(BaseSettings):

    # Database
    DB_HOST: str
    DB_PORT: int = 3306
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str = ""

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
# open ai
    GOOGLE_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

