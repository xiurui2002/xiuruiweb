from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=64)
    username = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.username


class Story(models.Model):
    CATEGORY_OPTIONS = [
        ("pol", "Politics"),
        ("art", "Art"),
        ("tech", "Technology"),
        ("trivia", "Trivia"),
    ]
    REGION_OPTIONS = [
        ("uk", "United Kingdom"),
        ("eu", "Europe"),
        ("w", "World"),
    ]
    headline = models.CharField(max_length=64)
    category = models.CharField(max_length=16, choices=CATEGORY_OPTIONS)
    region = models.CharField(max_length=16, choices=REGION_OPTIONS)
    author = models.CharField(max_length=64)
    date = models.DateField("story date")
    details = models.CharField(max_length=128)

    def __str__(self):
        return self.headline


class Agency(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField()
    code = models.CharField(max_length=10, unique=True)
