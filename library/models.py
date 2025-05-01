import requests
from bs4 import BeautifulSoup
from django.db import models
from django.utils.text import slugify
from simple_name_parser import NameParser

from accounts.models import CustomUser


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey('Author', on_delete=models.CASCADE, blank=True,
                               null=True)
    url = models.URLField()
    slug = models.SlugField(unique=True, blank=True, null=True)
    collections = models.ManyToManyField('Collection', related_name='books',
                                         blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    @property
    def book_html(self):
        url = self.url
        base_url_end = url.find("pg")
        base_url = url[:base_url_end]
        response = requests.get(url)
        full_html = response.text
        body_close = full_html.find('</body>')
        start = full_html.find("<body>")
        text = full_html[start + 6: body_close]
        soup = BeautifulSoup(text, "html.parser")
        for img in soup.find_all("img"):
            img["src"] = base_url + img["src"]
        for section in soup.find_all("section", class_="pg-boilerplate"):
            section.decompose()
        return str(soup)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)[:50]
        super(Book, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Author(models.Model):
    full_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    middle_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        name_parser = NameParser()
        parts = name_parser.parse_name(self.full_name)
        self.first_name = parts.given_name
        self.middle_name = parts.middle_name
        self.last_name = parts.surname
        self.suffix = parts.suffix
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name


class Collection(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ReadingProgress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    scroll_position = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.book} -- Scroll-y position: {self.scroll_position}"

    class Meta:
        unique_together = ('user', 'book')