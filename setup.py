import re 
import os

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    install_requires = fh.read().splitlines()
with open("multporn/__init__.py", encoding='utf8') as fh:
    version = re.search(r'__version__ = "(.*?)"', fh.read()).group(1)

if not os.getenv('READTHEDOCS'):
    install_requires.append('python-snappy')

print(install_requires)
setuptools.setup(
    name="multporn",
    version=version,
    author="pyporn-san",
    author_email="pypornsan@gmail.com",
    description="python library used to interact with multporn.net via python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pyporn-san/Multporn",
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
    python_requires='>=3.8',
)
