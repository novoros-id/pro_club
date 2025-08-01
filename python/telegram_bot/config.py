from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    TELEGRAM_TOKEN: str
    TELEGRAM_USER: str
    TELEGRAM_JUST_QUESTIONS: bool
    LOG_FOLDER: str
    ZAKROMA_FOLDER: str
    TASK_FOLDER: str
    LOG_FOLDER_PIPELINE: str
    TEMP_TASK_FOLDER: str
    #TELEGRAM_CHAT_ID: str
    API_URL: str
    PROGRAM_UID: str
    TELEGRAM_PORT: int

    DEBUG_TELEGRAM_CHAT_ID: str
    DEBUG_REQUEST_ID: str

    model_config = SettingsConfigDict(env_file=".env",
                                      env_file_encoding='utf-8')

settings = Settings()