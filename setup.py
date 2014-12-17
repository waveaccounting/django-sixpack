from setuptools import setup, find_packages

install_reqs = ["Django>=1.4", "sixpack-client==1.0.0"]

setup(
    name='django-sixpack',
    version=__import__('djsixpack').__version__,
    author="Dan Langer",
    author_email='opensource@waveapps.com',
    include_package_data=True,
    zip_safe=True,
    packages=find_packages(),
    url='https://github.com/waveaccounting/django-sixpack',
    license='LICENSE',
    description='A django-friendly wrapper for sixpack-py',
    long_description=open('README.rst').read(),
    install_requires=install_reqs,
    tests_require=install_reqs + ["mock==1.0.1"],
    test_suite='runtests.runtests',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
    ),
)
