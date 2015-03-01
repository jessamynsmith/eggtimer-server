import django_filters
from rest_framework import serializers

from periods import models as period_models


class FlowEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = period_models.FlowEvent
        exclude = ('user',)

    def validate_clots(self, value):
        # TODO submit patch to drf to handle nullable fields and coerce like Django does?
        # Coerce empty values to None
        if not value:
            value = None
        return value


class FlowEventFilter(django_filters.FilterSet):
    min_timestamp = django_filters.DateTimeFilter(name="timestamp", lookup_type='gte')
    max_timestamp = django_filters.DateTimeFilter(name="timestamp", lookup_type='lte')

    class Meta:
        model = period_models.FlowEvent
        fields = ('min_timestamp', 'max_timestamp')


class StatisticsSerializer(serializers.ModelSerializer):

    class Meta:
        model = period_models.Statistics
        fields = ('average_cycle_length', 'predicted_events', 'first_date', 'first_day')
