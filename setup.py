import os
from setuptools import find_packages, setup

base = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(base, 'README.rst'), encoding='utf-8') as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='cloudflare-ddns',
    version='1.0.2',
    description='DDNS script to sync public IP address to CloudFlare dns records',
    long_description=README,
    url='https://github.com/shlinx/cloudflare-ddns',
    author='Shawn Lin',
    author_email='shawnxiaolin@gmail.com',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    include_package_data=True,
    license='MIT',
    keywords='cloudflare ddns',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'requests'
    ],
    entry_points={
        'console_scripts': [
            'cloudflare-ddns=cloudflare_ddns.cloudflare:main'
        ],
    }
)
