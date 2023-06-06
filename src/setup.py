from setuptools import setup, find_packages

with open("../README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name="HELM Deployment Toolkit",
    version="0.4.1",
    author="Akaishi Toshiya",
    author_email="Toshiya14@live.jp",
    license="MIT",
    description="A HELM Deployment toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/toshiya14/hdt",
    py_modules=["helmdt"],
    packages=find_packages(),
    install_requires=[requirements],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    entry_points="""
        [console_scripts]
        helmdt=helmdt:main
    """,
)
