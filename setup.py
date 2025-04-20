from setuptools import setup, find_packages

setup(
    name="axai-pg",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "psycopg2-binary",
        "SQLAlchemy",
        "pydantic",
        "python-dotenv",
        "loguru",
    ],
    python_requires=">=3.8",
) 