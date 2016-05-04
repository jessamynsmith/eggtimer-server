import django_filters
from rest_framework import serializers

from periods import models as period_models


class NullableEnumField(serializers.ChoiceField):
    """
    Field that handles empty entries for EnumFields
    """

    def __init__(self, enum, **kwargs):
        super(NullableEnumField, self).__init__(enum.choices(), allow_blank=True, required=False)

    def to_internal_value(self, data):
        if data == '' and self.allow_blank:
            return None

        return super(NullableEnumField, self).to_internal_value(data)


class FlowEventSerializer(serializers.ModelSerializer):
    clots = NullableEnumField(period_models.ClotSize)
    cramps = NullableEnumField(period_models.CrampLevel)

    class Meta:
        model = period_models.FlowEvent
        exclude = ('user',)


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
