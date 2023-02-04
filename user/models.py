from django.db import models
import uuid


class User(models.Model):
    section_choices = (
        ('العلمي', 'العلمي'),
        ('الأدبي', 'الأدبي'),
        ('الصناعي', 'الصناعي'),
    )

    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(unique=True, max_length=30, null=True, blank=True)
    password = models.TextField(null=True, blank=True)

    firstName = models.CharField(max_length=30, null=True, blank=True)
    lastName = models.CharField(max_length=30, null=True, blank=True)

    grade = models.IntegerField(null=True, blank=True)
    section = models.CharField(max_length=50, choices=section_choices, null=True, blank=True)

    def __str__(self):
        return f'{self.email}-{self.phone}'
