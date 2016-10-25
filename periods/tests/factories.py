import datetime
from django.contrib.auth import get_user_model
import factory
import pytz

from periods import models as period_models

PASSWORD = 'bogus_password'


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    first_name = u'Jessamyn'
    birth_date = pytz.utc.localize(datetime.datetime(1995, 3, 1))
    email = factory.Sequence(lambda n: "user_%d@example.com" % n)
    password = factory.PostGenerationMethodCall('set_password', PASSWORD)
    last_login = pytz.utc.localize(datetime.datetime(2015, 3, 1))


class FlowEventFactory(factory.DjangoModelFactory):
    class Meta:
        model = period_models.FlowEvent

    user = factory.SubFactory(UserFactory)
    timestamp = pytz.utc.localize(datetime.datetime(2014, 1, 31, 17, 0, 0))
    first_day = True
