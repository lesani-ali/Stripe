from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    FRONTEND_URL: str
    CURRENCY: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()