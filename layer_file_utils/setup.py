from setuptools import setup, find_packages

setup(
    name="layer-file-utils",
    version="0.1.0",
    description="Reusable file reading and text processing utilities",
    author="Hexango",
    packages=find_packages(),   # will find the 'file_utils' package
    install_requires=[
        "boto3>=1.26.0",
        "python-docx>=0.8.11",
        "PyPDF2>=3.0.0",
        "typing-extensions>=4.5.0",
        "pandas>=2.0.0",
        "openpyxl>=3.1.0",
        "python-pptx>=0.6.21",
        "langchain>=0.1.0",
        "requests>=2.31.0"
    ],
    python_requires='>=3.10',
)

# pip install -e .
