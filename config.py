import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_NAME = "finance.db"
DATABASE_PATH = os.path.join(BASE_DIR, DATABASE_NAME)


class Config:
    DEBUG = True
    TESTING = False
    DATABASE = DATABASE_PATH


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DATABASE = os.path.join(BASE_DIR, "test_finance.db")


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}