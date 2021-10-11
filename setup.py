import setuptools

with open("docs/index.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="islandora7-rest",
    version="3.0.5",
    author="Jeremy Keeler <jkeeler@ku.edu>, Tom Shorock <shorock@ku.edu>",
    description="Python client for discoverygarden/islandora_rest (for Islandora 7)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kulibraries/islandora7-rest",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    install_requires=['requests>=2.5,<3', 'python-dotenv'],
    python_requires='>=3'
)
