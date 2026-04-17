from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class UserProfile(models.Model):
    """Metadados de aprovação do usuário, separados do User nativo do Django."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Profile({self.user.username})"
