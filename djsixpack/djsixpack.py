import re
import logging

from sixpack import sixpack
from django.conf import settings
from requests.exceptions import RequestException

RE_FIRST_CAP = re.compile('(.)([A-Z][a-z]+)')
RE_ALL_CAP = re.compile('([a-z0-9])([A-Z])')
RE_TEST_NAME = re.compile('_test$')

logger = logging.getLogger('djsixpack')


class AlternativesAttributeSetterMeta(type):
    def __new__(mcs, name, bases, dct):
        alts = dct.get('alternatives', ()) or ()
        dct.update(dict((alt, alt) for alt in alts))
        return super(AlternativesAttributeSetterMeta, mcs).__new__(mcs, name, bases, dct)


class SixpackTest(object):
    __metaclass__ = AlternativesAttributeSetterMeta

    unique_attr = 'pk'
    host = None
    timeout = None
    control = None
    alternatives = None

    def __init__(self, instance):
        self._instance = instance
        self.host = self.host or getattr(settings, 'SIXPACK_HOST', sixpack.SIXPACK_HOST)
        self.timeout = self.timeout or getattr(settings, 'SIXPACK_TIMEOUT', sixpack.SIXPACK_TIMEOUT)

    @property
    def client_id(self):
        return self.get_client_id(self._instance)

    def _get_session(self, user_agent=None, ip_address=None):
        session_kwargs = {
            'options': {'host': self.host, 'timeout': self.timeout},
            'params': {'ip_address': ip_address, 'user_agent': user_agent},
            'client_id': self.client_id,
        }

        return sixpack.Session(**session_kwargs)

    def _get_experiment_name(self):
        # Converts CamelCase to snake_case and drops the trailing "_test"
        s1 = RE_FIRST_CAP.sub(r'\1_\2', self.__class__.__name__)
        name = RE_ALL_CAP.sub(r'\1_\2', s1).lower()
        return RE_TEST_NAME.sub('', name)

    def get_client_id(self, instance):
        if not self.unique_attr:
            raise ValueError('Need a unique_attr to compute the client ID')

        client_id = getattr(instance, self.unique_attr, None)
        if not client_id:
            raise ValueError('Unique_attr {0} does not yield a usable identifier'.format(self.unique_attr))

        return client_id

    def participate(self, force=None, user_agent=None, ip_address=None):
        if not self.host:
            try:
                if force in self.alternatives:
                    return force
                return self.alternatives[0]
            except TypeError:
                raise ValueError('No alternatives defined')

        session = self._get_session(user_agent, ip_address)
        experiment_name = self._get_experiment_name()

        try:
            resp = session.participate(experiment_name, self.alternatives, force)
        except RequestException:
            logger.exception("Error while trying to .participate")
            if force in self.alternatives:
                return force
            return self.alternatives[0]
        else:
            return resp['alternative']['name']

    def convert(self, kpi=None):
        if not self.host:
            return True

        session = self._get_session()
        experiment_name = self._get_experiment_name()
        try:
            resp = session.convert(experiment_name)
        except RequestException as e:
            logger.exception("Error while trying to .convert: {err}".format(err=e))
            return False
        else:
            return resp['status'] == 'ok'
