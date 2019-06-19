from django.db import models

from django.utils.timezone import datetime
from django.contrib.auth.models import User


class Message(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    date = models.DateTimeField(default=datetime.now())
    content = models.CharField(max_length=3000)
    toxic_ratio = models.CharField(max_length=10)
    severe_ratio = models.CharField(max_length=10)
    obscene_ratio = models.CharField(max_length=10)
    threat_ratio = models.CharField(max_length=10)
    insult_ratio = models.CharField(max_length=10)
    hate_ratio = models.CharField(max_length=10)
    L_toxic_ratio = models.CharField(max_length=10, default='')
    L_severe_ratio = models.CharField(max_length=10, default='')
    L_obscene_ratio = models.CharField(max_length=10, default='')
    L_threat_ratio = models.CharField(max_length=10, default='')
    L_insult_ratio = models.CharField(max_length=10, default='')
    L_hate_ratio = models.CharField(max_length=10, default='')
    toxic_words = models.CharField(max_length=1000, default='')
    severe_words = models.CharField(max_length=1000, default='')
    obscene_words = models.CharField(max_length=1000, default='')
    threat_words = models.CharField(max_length=1000, default='')
    insult_words = models.CharField(max_length=1000, default='')
    hate_words = models.CharField(max_length=1000, default='')
    toxic_comment = models.BooleanField(default=False)

    def __str__(self):
        return self.owner.username + str(self.date)

    class Meta:
        ordering = ['-id']
