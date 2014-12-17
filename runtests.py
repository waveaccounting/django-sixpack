import os
import sys

from django.conf import settings


if not settings.configured:
    settings_dict = dict(
        INSTALLED_APPS=("djsixpack",),
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
        MIDDLEWARE_CLASSES = (
             'django.contrib.sessions.middleware.SessionMiddleware',
             'django.middleware.common.CommonMiddleware',
             'django.middleware.csrf.CsrfViewMiddleware',
             'django.contrib.auth.middleware.AuthenticationMiddleware',
             'django.contrib.messages.middleware.MessageMiddleware',
             'django.middleware.clickjacking.XFrameOptionsMiddleware',
        )
    )

    settings.configure(**settings_dict)


def runtests(*test_args):
    if not test_args:
        test_args = ['djsixpack']

    parent = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, parent)

    try:
        from django import setup
        setup()
    except ImportError:
        pass

    from django.test.runner import DiscoverRunner
    from django.test.utils import setup_test_environment
    setup_test_environment()

    failures = DiscoverRunner(pattern="*tests.py", verbosity=1, interactive=True, failfast=False).run_tests(test_args)
    sys.exit(failures)

if __name__ == '__main__':
    runtests()
