from rest_framework import serializers


class FileImportSerializer(serializers.Serializer):
    entity_type = serializers.ChoiceField(choices=['students', 'employees'])
    file = serializers.FileField()

    def validate_file(self, value):
        filename = value.name.lower()
        if not (filename.endswith('.csv') or filename.endswith('.xlsx')):
            raise serializers.ValidationError(
                "Formato de arquivo inválido. Envie um arquivo .csv ou .xlsx."
            )
        return value
