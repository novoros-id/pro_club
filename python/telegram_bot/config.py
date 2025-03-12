from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    TELEGRAM_TOKEN: str
    TELEGRAM_CHAT_ID: str
    API_URL: str
    PROGRAM_UID: str

    model_config = SettingsConfigDict(env_file=".env",
                                      env_file_encoding='utf-8')

settings = Settings()