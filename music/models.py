import math
from time import strftime, gmtime

from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone
import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from .utils import generate_file_name

def song_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return "songs/{0}/{1}".format(
        strftime("%Y/%m/%d"), generate_file_name() + "." + filename.split(".")[-1]
    )


# Create your models here.
class User(AbstractUser):
    username = None
    name = models.CharField(max_length=100)
    first_name = None
    last_name = None
    email = models.EmailField(
        unique=True,
        blank=False,
        error_messages={"unique": "A user with that email already exists.",},
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __unicode__(self):
        return self.email


class Genre(models.Model):
    name = models.CharField(max_length=50)
    thumbnail = models.ImageField(upload_to="genres", default="default.jpeg")


class Artist(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Artist, self).save(*args, **kwargs)


class Song(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    audio_id = models.TextField()
    title = models.CharField(max_length=200, verbose_name="Song name")
    thumbnail = models.ImageField(upload_to="thumbnails", blank=False)
    song = models.FileField(upload_to=song_directory_path)
    # audio_location = models.CharField(max_length=255)
    genre = models.ForeignKey(Genre, on_delete=models.DO_NOTHING)
    artists = models.ManyToManyField(Artist, related_name="songs")
    size = models.IntegerField(default=0)
    playtime = models.CharField(max_length=10, default="0.00")
    created_at = models.DateTimeField(verbose_name="Created At", default=timezone.now)
    likes = models.ManyToManyField(User, related_name="music_likes")

    @property
    def duration(self):
        return str(strftime("%H:%M:%S", gmtime(float(self.playtime))))

    @property
    def file_size(self):
        if self.size == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(self.size, 1024)))
        p = math.pow(1024, i)
        s = round(self.size / p, 2)
        return "%s %s" % (s, size_name[i])

class Watchlater(models.Model):
    watch_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video_id = models.CharField(max_length=10000, default="")


class History(models.Model):
    hist_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    music_id = models.CharField(max_length=10000, default="")


class Channel(models.Model):
    channel_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=1000)
    music = models.CharField(max_length=10000)

