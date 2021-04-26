from os import path
from setuptools import setup, find_packages


def read(name):
    return open(path.join(path.dirname(__file__), name)).read()

setup(
    name='django-url-migration',
    version='0.2.2',
    description='Advanced url migration application',
    long_description=read('README.rst'),
    author='Social WiFi',
    author_email='kontakt@socialwifi.com',
    url='https://github.com/socialwifi/django-url-migration',
    packages=find_packages(exclude=["url_migration_demo"]),
    install_requires=[
        'Django',
    ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
