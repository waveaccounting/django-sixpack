from mock import Mock, patch, call

from django.test import TestCase

from djsixpack.djsixpack import SixpackTest
from djsixpack.models import SixpackParticipant
from djsixpack.tests.factories import SixpackParticipantFactory


class ClientIdTest(TestCase):

    def test_client_id_property_calls_method(self):
        t = SixpackTest(Mock())
        t.get_client_id = Mock()

        t.client_id
        self.assertTrue(t.get_client_id.called)

    def test_client_id_no_attr_set(self):
        t = SixpackTest(Mock())
        t.unique_attr = None

        with self.assertRaises(ValueError):
            t.client_id

    def test_client_id_no_usable_identifier(self):
        t = SixpackTest(Mock(pk=None))

        with self.assertRaises(ValueError):
            t.client_id

    def test_client_id_uses_set_attr(self):
        t = SixpackTest(Mock(pk=5))

        self.assertEqual(t.client_id, 5)


class ParticipateTest(TestCase):

    def test_participate_errors_when_no_alternatives(self):
        mock_user = Mock(pk=10)

        class NoAltsTest(SixpackTest):
            alternatives = ()

        expt = NoAltsTest(mock_user)
        self.assertRaises(ValueError, expt.participate)

    def test_participate_returns_default_when_no_host_set(self):
        mock_user = Mock(pk=10)

        class DefaultTest(SixpackTest):
            alternatives = ('FIRST', 'SECOND')

        with patch('djsixpack.djsixpack.sixpack') as sp_mock:
            with self.settings(SIXPACK_HOST=None):
                expt = DefaultTest(mock_user)
                alternative = expt.participate()

        self.assertEqual(alternative, 'FIRST')
        self.assertFalse(sp_mock.participate.called)

    def test_participate_returns_force_when_no_host_set_and_force_in_alternatives(self):
        mock_user = Mock(pk=10)

        class DefaultTest(SixpackTest):
            alternatives = ('FIRST', 'SECOND')

        with patch('djsixpack.djsixpack.sixpack') as sp_mock:
            with self.settings(SIXPACK_HOST=None):
                expt = DefaultTest(mock_user)
                alternative = expt.participate(force='SECOND')

        self.assertEqual(alternative, 'SECOND')
        self.assertFalse(sp_mock.participate.called)

    def test_participate_returns_default_when_no_host_set_and_force_not_in_alternatives(self):
        mock_user = Mock(pk=10)

        class DefaultTest(SixpackTest):
            alternatives = ('FIRST', 'SECOND')

        with patch('djsixpack.djsixpack.sixpack') as sp_mock:
            with self.settings(SIXPACK_HOST=None):
                expt = DefaultTest(mock_user)
                alternative = expt.participate(force='THIRD')

        self.assertEqual(alternative, 'FIRST')
        self.assertFalse(sp_mock.participate.called)

    def test_participate_calls_library(self):
        mock_user = Mock(pk=10)

        class DefaultTest(SixpackTest):
            alternatives = ('FIRST', 'SECOND')

        with patch('djsixpack.djsixpack.sixpack') as sp_mock:
            expt = DefaultTest(mock_user)
            expt.participate()

        self.assertEqual(
            sp_mock.Session.call_args_list,
            [call(
                params={'ip_address': None, 'user_agent': None},
                options={'host': sp_mock.SIXPACK_HOST, 'timeout': sp_mock.SIXPACK_TIMEOUT},
                client_id=10
            )]
        )
        self.assertEqual(
            sp_mock.Session.return_value.participate.call_args_list,
            [call('default', ('FIRST', 'SECOND'), force=None, bucket=None, prefetch=False)]
        )

    def test_force_doesnt_record_participation(self):
        mock_user = Mock(pk=10)

        class DefaultTest(SixpackTest):
            alternatives = ('FIRST', 'SECOND')
            local = True

        class MockSession(object):
            def participate(self, experiment_name, alternatives, force, prefetch, bucket):
                return {
                    'alternative': {'name': 'SECOND'}
                }
        mock_session = MockSession()

        with patch('djsixpack.djsixpack.sixpack'):
            with self.settings(SIXPACK_HOST=None):
                expt = DefaultTest(mock_user)
                with patch.object(SixpackTest, '_get_session', return_value=mock_session):
                    expt.participate(force='SECOND', bucket='THIRD')

        self.assertFalse(SixpackParticipant.objects.all().exists())

    def test_force_overrides_bucket(self):
        mock_user = Mock(pk=10)

        class DefaultTest(SixpackTest):
            alternatives = ('FIRST', 'SECOND', 'THIRD')
            local = True

        class MockSession(object):
            def participate(self, experiment_name, alternatives, force, prefetch, bucket):
                return {
                    'alternative': {'name': 'SECOND'}
                }
        mock_session = MockSession()

        with patch('djsixpack.djsixpack.sixpack'):
            with self.settings(SIXPACK_HOST=None):
                expt = DefaultTest(mock_user)
                with patch.object(SixpackTest, '_get_session', return_value=mock_session):
                    bucket = expt.participate(force='SECOND', bucket='THIRD')

        self.assertTrue(bucket, 'SECOND')

    def test_participate_tracks_participation_locally(self):
        mock_user = Mock(pk=10)

        class DefaultTest(SixpackTest):
            alternatives = ('FIRST', 'SECOND')
            local = True

        class MockSession(object):
            def participate(self, experiment_name, alternatives, force, prefetch, bucket):
                return {
                    'alternative': {'name': 'SECOND'}
                }

        mock_session = MockSession()

        with patch.object(SixpackTest, '_get_session', return_value=mock_session):
            expt = DefaultTest(mock_user)
            expt.participate()

        self.assertTrue(SixpackParticipant.objects.filter(unique_attr=10, experiment_name='default').exists())

    def test_participate_is_called_twice_for_local_test(self):
        mock_user = Mock(pk=10)

        class DefaultTest(SixpackTest):
            alternatives = ('FIRST', 'SECOND')
            local = True

        class MockSession1(object):
            def participate(self, experiment_name, alternatives, force, prefetch, bucket):
                return {
                    'alternative': {'name': 'FIRST'}
                }
        mock_session1 = MockSession1()

        class MockSession2(object):
            def participate(self, experiment_name, alternatives, force, prefetch, bucket):
                return {
                    'alternative': {'name': 'FIRST'}
                }
        mock_session2 = MockSession2()

        with patch('djsixpack.djsixpack.sixpack'):
            with self.settings(SIXPACK_HOST=None):
                expt = DefaultTest(mock_user)
                with patch.object(SixpackTest, '_get_session', return_value=mock_session1):
                    expt.participate(bucket='FIRST')
                with patch.object(SixpackTest, '_get_session', return_value=mock_session2):
                    bucket = expt.participate(bucket='SECOND')

        self.assertEquals(SixpackParticipant.objects.all().count(), 1)
        self.assertEquals(bucket, 'FIRST')
        self.assertEquals(SixpackParticipant.objects.all()[0].bucket, 'FIRST')


class ExperimentNameTest(TestCase):

    def test_to_snake(self):
        class CompoundNameTest(SixpackTest):
            pass

        expt = CompoundNameTest(Mock)
        self.assertEqual(expt._get_experiment_name(), 'compound_name')

    def test_name_drops_test(self):
        class CompoundNameTest(SixpackTest):
            pass

        expt = CompoundNameTest(Mock)
        self.assertNotIn('_test', expt._get_experiment_name())


class AlternativesSetAsAttributesTest(TestCase):

    def test_alternatives_are_set_as_attributes(self):
        class AltTest(SixpackTest):
            alternatives = ('FIRST', 'SECOND')

        self.assertTrue(hasattr(AltTest, 'FIRST'))
        self.assertTrue(hasattr(AltTest, 'SECOND'))


class GetParticipantBucketTest(TestCase):

    def test_get_bucket__single_record(self):
        mock_user = Mock(pk=10)

        class GetBucketTest(SixpackTest):
            alternatives = ('FIRST', 'SECOND')

        expt = GetBucketTest(mock_user)
        expt.local = True
        expt.participate(bucket='FIRST')

        self.assertEquals(expt.get_participant_bucket(), 'FIRST')

    def test_get_bucket__zero_records(self):
        mock_user = Mock(pk=10)

        class GetBucketTest(SixpackTest):
            alternatives = ('FIRST', 'SECOND')

        expt = GetBucketTest(mock_user)
        self.assertIsNone(expt.get_participant_bucket())

    def test_get_bucket__multiple_records(self):
        mock_user = Mock(pk=10)

        class GetBucketTest(SixpackTest):
            alternatives = ('FIRST', 'SECOND')

        expt = GetBucketTest(mock_user)
        expt.local = True
        expt.participate(bucket='FIRST')

        # Insert an extra record to mess things up.
        SixpackParticipantFactory(experiment_name='get_bucket', unique_attr=10, bucket='SECOND')

        self.assertEquals(expt.get_participant_bucket(), 'FIRST')

        record_count = SixpackParticipant.objects.filter(experiment_name='get_bucket', unique_attr=10).count()
        self.assertEquals(record_count, 1)


class ConvertTest(TestCase):

    def test_convert_doesnt_call_library_when_no_host(self):
        mock_user = Mock(pk=10)

        class DefaultTest(SixpackTest):
            alternatives = ('FIRST', 'SECOND')

        with patch('djsixpack.djsixpack.sixpack') as sp_mock:
            with self.settings(SIXPACK_HOST=None):
                expt = DefaultTest(mock_user)
                expt.convert()

        self.assertFalse(sp_mock.Session().convert.called)

    def test_convert_calls_library(self):
        mock_user = Mock(pk=10)

        class DefaultTest(SixpackTest):
            alternatives = ('FIRST', 'SECOND')

        with patch('djsixpack.djsixpack.sixpack') as sp_mock:
            expt = DefaultTest(mock_user)
            expt.convert(kpi='cats')

        self.assertEqual(
            sp_mock.Session().convert.call_args_list,
            [call('default')]
        )
