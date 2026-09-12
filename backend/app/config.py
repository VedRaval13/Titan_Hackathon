from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = 'sqlite+aiosqlite:///./titans.db'
    JIRA_BASE_URL: str = ''
    JIRA_EMAIL: str = ''
    JIRA_API_TOKEN: str = ''
    GEMINI_API_KEY: str = ''
    JWT_SECRET_KEY: str = 'dev-secret-key-change-in-production'
    JWT_ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    FRONTEND_URL: str = 'http://localhost:5173'
    MAX_WORKLOAD_SCORE: float = 8.0
    JIRA_PROJECT_KEY: str = ''

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

settings = Settings()
