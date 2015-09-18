from factory import DjangoModelFactory

from djsixpack.models import SixpackParticipant


class SixpackParticipantFactory(DjangoModelFactory):
    class Meta:
        model = SixpackParticipant

    experiment_name = 'Science Experiment'
    unique_attr = 1
    bucket = 'Bucket A'
