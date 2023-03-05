from django.db import models

# Create your models here.

class Search(models.Model):
    prompt = models.CharField(max_length=200)
    last_search = models.DateTimeField("searh date")
    data = models.TextField()

    def __str__(self):
        return self.prompt
    