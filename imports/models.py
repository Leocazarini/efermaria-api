from django.conf import settings
from django.db import models


class ImportLog(models.Model):
    SOURCE_FILE = 'file'
    SOURCE_EXTERNAL = 'external'
    SOURCE_CHOICES = [(SOURCE_FILE, 'Arquivo'), (SOURCE_EXTERNAL, 'API Externa')]

    ENTITY_STUDENTS = 'students'
    ENTITY_EMPLOYEES = 'employees'
    ENTITY_CHOICES = [
        (ENTITY_STUDENTS, 'Alunos'),
        (ENTITY_EMPLOYEES, 'Funcionários'),
    ]

    entity_type   = models.CharField(max_length=20, choices=ENTITY_CHOICES)
    source        = models.CharField(max_length=20, choices=SOURCE_CHOICES, default=SOURCE_FILE)
    filename      = models.CharField(max_length=255, blank=True)
    imported_by   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    imported_at   = models.DateTimeField(auto_now_add=True)
    total_rows    = models.IntegerField(default=0)
    created_count = models.IntegerField(default=0)
    updated_count = models.IntegerField(default=0)
    error_count   = models.IntegerField(default=0)
    errors        = models.JSONField(default=list)  # [{'row': N, 'reason': '...'}]

    def __str__(self):
        return f"ImportLog #{self.pk} — {self.entity_type} ({self.imported_at})"
