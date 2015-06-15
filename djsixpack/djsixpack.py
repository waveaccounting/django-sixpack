import re
import logging

from sixpack import sixpack
from django.conf import settings
from requests.exceptions import RequestException

from models import SixpackParticipant

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
    local = False
    server = True

    def __init__(self, instance, local=None, server=None):
        self._instance = instance
        self.host = self.host or getattr(settings, 'SIXPACK_HOST', sixpack.SIXPACK_HOST)
        self.timeout = self.timeout or getattr(settings, 'SIXPACK_TIMEOUT', sixpack.SIXPACK_TIMEOUT)
        if local is not None:
            self.local = local
        if server is not None:
            self.server = server

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

    def get_participant_bucket(self):
        try:
            participant = SixpackParticipant.objects.get(unique_attr=self.client_id, experiment_name=self._get_experiment_name())
        except SixpackParticipant.DoesNotExist:
            return None
        except SixpackParticipant.MultipleObjectsReturned:
            # clean up duplicate entries
            duplicates = SixpackParticipant.objects.filter(unique_attr=self.client_id, experiment_name=self._get_experiment_name())
            for dup in duplicates[1:]:
                dup.delete()
            return duplicates[0].bucket
        return participant.bucket

    def participate(self, force=None, user_agent=None, ip_address=None, prefetch=False, bucket=None):
        if not self.host and not self.local:
            try:
                if force in self.alternatives:
                    return force
                return self.alternatives[0]
            except TypeError:
                raise ValueError('No alternatives defined')

        session = self._get_session(user_agent, ip_address)
        experiment_name = self._get_experiment_name()
        chosen_alternative = bucket

        if self.local and not self.server:
            prefetch = True

        try:
            resp = session.participate(experiment_name, self.alternatives, force=force, prefetch=prefetch, bucket=bucket)
        except RequestException:
            logger.exception("Error while trying to .participate")
            if force in self.alternatives:
                chosen_alternative = force
            else:
                chosen_alternative = self.alternatives[0]
        else:
            chosen_alternative = resp['alternative']['name']
        finally:
            if self.local and chosen_alternative:

                # Record the bucket in the database if one doesn't already exist.
                if not SixpackParticipant.objects.filter(unique_attr=self.client_id, experiment_name=experiment_name).exists():
                    SixpackParticipant.objects.get_or_create(unique_attr=self.client_id, experiment_name=experiment_name, bucket=chosen_alternative)

                # Check for duplicate records and delete them.
                duplicates = SixpackParticipant.objects.filter(unique_attr=self.client_id, experiment_name=experiment_name).order_by('id')
                for dup in duplicates[1:]:
                    dup.delete()

        return chosen_alternative

    def convert(self, kpi=None):
        if not self.host:
            return True

        import ipdb; ipdb.set_trace()
        session = self._get_session()
        experiment_name = self._get_experiment_name()
        try:
            resp = session.convert(experiment_name)

            if self.local:
                participant_exists = SixpackParticipant.objects.filter(unique_attr=self.client_id, experiment_name=experiment_name).exists()
                if participant_exists:
                    participant = SixpackParticipant.objects.filter(unique_attr=self.client_id, experiment_name=experiment_name)[0]
                    participant.converted = True
                    participant.save()

        except RequestException as e:
            logger.exception("Error while trying to .convert: %s", e)
            return False
        else:
            return resp['status'] == 'ok'
