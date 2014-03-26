from mock import Mock, patch, call

from django.test import TestCase

from djsixpack.djsixpack import SixpackTest


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
            [call('default', ('FIRST', 'SECOND'), None)]
        )

        class ConvertTest(TestCase):

            def test_convert_doesnt_call_library_when_no_host(self):
                Mock(pk=10)

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
