from setuptools import setup, find_packages

setup(
    name="foretale-db-utils",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy>=2.0.0",
        "pandas>=2.2.0",
        "python-dotenv>=1.0.0",
        "pyodbc>=5.0.1",
    ],
    author="Foretale Team",
    author_email="your.email@example.com",  # Update this with your email
    description="Database utilities for the Foretale application",
    long_description=open("README.md").read() if open("README.md").read() else "Database utilities for the Foretale application",
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/foretale-db-api",  # Update this with your repository URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
) 