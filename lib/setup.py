from setuptools import setup, find_packages

setup(
    name="email_service",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "django",
    ],
)