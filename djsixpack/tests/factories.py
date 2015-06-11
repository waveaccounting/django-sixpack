from factory import Factory

from djsixpack.models import SixpackParticipant


class SixpackParticipantFactory(Factory):

    FACTORY_FOR = SixpackParticipant

    experiment_name = 'Science Experiment'
    unique_attr = 1
    bucket = 'Bucket A'
