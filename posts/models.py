from django.db import models
from django.contrib import admin

class Post(models.Model):
    title = models.CharField(max_length=20)
    content = models.TextField()
    author = models.CharField(max_length=15)

    def __str__(self):
        return self.title + ' - written by ' + self.author
    

admin.site.register(Post)