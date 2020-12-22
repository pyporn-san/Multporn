import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    install_requires = fh.read().splitlines()
print(install_requires)
setuptools.setup(
    name="Multporn",
    version="0.0.1",
    author="pyporn-san",
    author_email="pypornsan@gmail.com",
    description="python library used to interact with multporn.net via python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    install_requires=install_requires,
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Natural Language :: English",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities"
    ],
    python_requires='>=3.6',
)
