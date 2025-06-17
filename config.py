import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///inventory.db")

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "postgresql://nithinr07:hs84wisBvoHIghkJsjYEHmjcLYwfju2r@dpg-d18ptqbipnbc7394v5rg-a/hw_inventory")  # must be set on Render

config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}
