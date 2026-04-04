from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding= "utf-8"
    )
    
    # prevents the key from being accidently printed in logs or tracebacks
    secret_key : SecretStr
    # if not found in .env then default
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30 
    
# this method is better than os.getenv ( type hinting in pydantic-settings, riase error if missing keys , SecretStr and automatic defaults)    
settings = Settings()
