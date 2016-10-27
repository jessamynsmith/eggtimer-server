from django.test import TestCase
from rest_framework.renderers import JSONRenderer

from periods import models as period_models
from periods.serializers import FlowEventSerializer, NullableEnumField
from periods.tests.factories import FlowEventFactory


class TestNullableEnumField(TestCase):

    def test_to_internal_value_empty(self):
        field = NullableEnumField(period_models.ClotSize)

        result = field.to_internal_value('')

        self.assertIsNone(result)

    def test_to_internal_value_value(self):
        field = NullableEnumField(period_models.ClotSize)

        result = field.to_internal_value('1')

        self.assertEqual(1, result)


class TestFlowEventViewSet(TestCase):

    def setUp(self):
        FlowEventFactory()
        self.serializer = FlowEventSerializer(instance=period_models.FlowEvent.objects.first())

    def test_serialization(self):
        result = JSONRenderer().render(self.serializer.data)

        expected = (b'{"id":[\d]+,"clots":null,"cramps":null,"timestamp":"2014-01-31T17:00:00Z",'
                    b'"first_day":true,"level":2,"color":2,"comment":null}')
        self.assertRegex(result, expected)
