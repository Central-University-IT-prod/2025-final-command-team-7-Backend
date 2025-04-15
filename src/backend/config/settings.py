from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_DSN: str
    JWT_SECRET: str

    TMDB_API_KEY: str
    TMDB_BASE_URL: str

    KINOPOISK_UNOFFICIAL_BASE_URL: str
    KINOPOISK_UNOFFICIAL_KEY: str
    KINOPOISK_DEV_BASE_URL: str
    KINOPOISK_DEV_KEY: str

    GPT_BASE: str
    GPT_API_KEY: str

    AWS_ENDPOINT_URL: str
    AWS_KEY_ID: str
    AWS_ACCESS_KEY: str

    FILES_BASE_URL: str

    model_config = SettingsConfigDict(extra="allow", case_sensitive=False)
