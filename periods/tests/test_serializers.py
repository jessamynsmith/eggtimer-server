from django.test import TestCase
from rest_framework.renderers import JSONRenderer

from periods import models as period_models
from periods.serializers import FlowEventSerializer
from periods.tests.factories import FlowEventFactory


class TestFlowEventViewSet(TestCase):

    def setUp(self):
        FlowEventFactory()

    def test_serialization(self):
        serializer = FlowEventSerializer(instance=period_models.FlowEvent.objects.all()[0])
        result = JSONRenderer().render(serializer.data)

        self.assertEqual({}, result)
