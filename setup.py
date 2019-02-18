import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="phial",
    version="0.1.0",
    author="Madelyn Eriksen",
    author_email="hello@madelyneriksen.com",
    description="A tiny ASGI framework.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/madelyneriksen/phial",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
