from setuptools import setup, find_packages

setup(
    name='codespeed',
    version='0.11.0',
    author='Miquel Torres',
    author_email='tobami@gmail.com',
    url='https://github.com/tobami/codespeed',
    download_url="https://github.com/tobami/codespeed/tags",
    license='GNU Lesser General Public License version 2.1',
    keywords=["benchmarking", "visualization"],
    install_requires=['django>=1.6,<1.9', 'isodate>=0.4.7,<0.6'],
    packages=find_packages(exclude=['ez_setup', 'codespeed_project']),
    description='A web application to monitor and analyze the performance of your code',
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ]
)
