import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="avalet", # Replace with your own username
    version="0.1.0",
    author="Alejandro Torres",
    author_email="alejandro@atorresg.com",
    description="Avalet",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/atorresg/avalet",
    install_requires = ["termcolor","unidecode","pathlib"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
    ],
    python_requires='>=3.7',
)