from rest_framework import serializers


class AppointmentQuerySerializer(serializers.Serializer):
    date_begin = serializers.DateField()
    date_end = serializers.DateField()
    infirmaries = serializers.ListField(child=serializers.CharField(), min_length=1)
    search = serializers.CharField(required=False, allow_blank=True, default='')

    def validate(self, data):
        if data['date_end'] < data['date_begin']:
            raise serializers.ValidationError(
                {'date_end': 'date_end não pode ser anterior a date_begin.'}
            )
        return data


class NurseStatsSerializer(serializers.Serializer):
    nurse = serializers.CharField()
    count = serializers.IntegerField()
