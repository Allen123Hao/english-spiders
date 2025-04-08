from setuptools import setup, find_packages

setup(
    name="dict_data_importer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy",
        "ijson",
        "python-dotenv",  # 如果使用了 .env 文件
    ],
    entry_points={
        'console_scripts': [
            'dict-importer=dict_data_importer.data_importer.__main__:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="Cambridge Dictionary Data Importer",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
) 