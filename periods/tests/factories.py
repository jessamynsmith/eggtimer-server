import datetime
from django.contrib.auth import get_user_model
import factory

from periods import models as period_models


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    first_name = u'Jessamyn'
    email = factory.Sequence(lambda n: "user_%d@example.com" % n)


class FlowEventFactory(factory.DjangoModelFactory):
    class Meta:
        model = period_models.FlowEvent

    user = factory.SubFactory(UserFactory)
    timestamp = datetime.datetime(2014, 1, 31)
    first_day = True
