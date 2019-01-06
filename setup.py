#!/usr/bin/env python3

from distutils.core import setup

install_requires = [
    'Django>=2.1',
    'gnupg>=2.3',
    'six>=1.11'
]

setup(
    name='django-reprepro',
    version='0.1.0b1',
    description='',
    author='Mathias Ertl',
    author_email='mati@er.tl',
    url='https://github.com/mathiasertl/django-reprepro',
    packages=[
        'django_reprepro',
        'django_reprepro.management',
        'django_reprepro.management.commands',
        'django_reprepro.migrations',
    ],
    install_requires=install_requires,
    classifiers=[
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
