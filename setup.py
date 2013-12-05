from setuptools import setup, find_packages

setup(
    name='django-sixpack',
    version=__import__('identity').__version__,
    author=open('AUTHORS').read(),
    author_email='dan@waveapps.com',
    include_package_data=True,
    zip_safe=True,
    packages=find_packages(),
    url='https://github.com/waveaccounting/django-sixpack',
    license='LICENSE',
    description='A opinionated django-focused wrapper for sixpack-py',
    long_description=open('README.md').read(),
    install_requires=["Django>=1.4", "sixpack-client==1.0.0"],
    tests_require=["Django>=1.4", "mock==1.0.1", "sixpack-client==1.0.0"],
    test_suite='runtests.runtests',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Django Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
    ),
)
