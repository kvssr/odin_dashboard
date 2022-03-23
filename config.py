import os


class Config:
    DEBUG = False
    DEVELOPMENT = False
    SECRET_KEY = os.getenv("SECRET_KEY", "C7baf5kXsK7ahGnYYCQ7L6BQXZ9RyL9vENJ8")
    CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"): # Fix for the heroku string
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)


class ProductionConfig(Config):
    ENV = 'production'
    pass


class StagingConfig(Config):
    ENV = 'staging'
    DEBUG = True


class DevelopmentConfig(Config):
    ENV = 'development'
    DEBUG = True
    DEVELOPMENT = True


class TestingConfig(Config):
    ENV = 'testing'
    TESTING = True
