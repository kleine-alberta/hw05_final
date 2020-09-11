from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    def __str__(self):
        return self.title

    title = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(unique='title', max_length=50)
    description = models.TextField(blank=True, null=True)


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="posts")
    group = models.ForeignKey(Group,
                              on_delete=models.SET_NULL,
                              blank=True,
                              null=True,
                              related_name="groups")
    image = models.ImageField(upload_to='posts/',
                              blank=True,
                              null=True,
                              verbose_name="изображение")

    def __str__(self):
        return f'Post text={self.text[:100]}'

    class Meta:
        ordering = ["-pub_date"]


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.SET_NULL,
                             null=True,
                             related_name="comments")
    author = models.ForeignKey(User,
                               on_delete=models.SET_NULL,
                               null=True,
                               related_name="comments")
    text = models.TextField()
    created = models.DateTimeField("date published", auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.SET_NULL,
                             null=True,
                             related_name="follower")
    author = models.ForeignKey(User,
                               on_delete=models.SET_NULL,
                               null=True,
                               related_name="following")

    class Meta:
        unique_together = ("user", "author")
