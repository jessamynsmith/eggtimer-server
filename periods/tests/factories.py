import datetime
from django.contrib.auth import get_user_model
import factory
import pytz

from periods import models as period_models


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    first_name = u'Jessamyn'
    birth_date = pytz.timezone("US/Eastern").localize(datetime.datetime(1995, 3, 1))
    email = factory.Sequence(lambda n: "user_%d@example.com" % n)
    last_login = pytz.timezone("US/Eastern").localize(datetime.datetime(2015, 3, 1))


class FlowEventFactory(factory.DjangoModelFactory):
    class Meta:
        model = period_models.FlowEvent

    user = factory.SubFactory(UserFactory)
    timestamp = pytz.timezone("US/Eastern").localize(datetime.datetime(2014, 1, 31))
    first_day = True
