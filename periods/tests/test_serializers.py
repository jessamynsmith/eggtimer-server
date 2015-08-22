from django.test import TestCase
from rest_framework.renderers import JSONRenderer

from periods import models as period_models
from periods.serializers import FlowEventSerializer
from periods.tests.factories import FlowEventFactory


class TestFlowEventViewSet(TestCase):

    def setUp(self):
        FlowEventFactory()
        self.serializer = FlowEventSerializer(instance=period_models.FlowEvent.objects.all()[0])

    def test_serialization(self):
        result = JSONRenderer().render(self.serializer.data)

        expected = (b'{"id":[\d]+,"timestamp":"2014-01-31T17:00:00Z","first_day":true,"level":2,'
                    b'"color":2,"clots":null,"cramps":null,"comment":null}')
        self.assertRegex(result, expected)

    def test_validate_clots_no_value(self):
        result = self.serializer.validate_clots(None)

        self.assertEqual(None, result)

    def test_validate_clots_empty_value(self):
        result = self.serializer.validate_clots('')

        self.assertEqual(None, result)

    def test_validate_clots_zero_value(self):
        result = self.serializer.validate_clots(0)

        self.assertEqual(0, result)

    def test_validate_clots_valid_value(self):
        result = self.serializer.validate_clots(1)

        self.assertEqual(1, result)

    def test_validate_cramps_zero_value(self):
        result = self.serializer.validate_cramps(0)

        self.assertEqual(0, result)

    def test_validate_cramps_valid_value(self):
        result = self.serializer.validate_cramps(1)

        self.assertEqual(1, result)
