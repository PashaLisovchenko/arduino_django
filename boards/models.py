from django.db import models
from django.core.urlresolvers import reverse
from django.utils.text import slugify


class Languages(models.Model):
    name = models.CharField(max_length=48)

    def __str__(self):
        return self.name


class Board(models.Model):
    name = models.CharField(max_length=48)
    slug = models.SlugField(max_length=250,
                            unique=True,
                            blank=True)
    processor = models.CharField(max_length=48)
    programming_languages = models.ManyToManyField(Languages,
                                                   related_name='prog_lang',
                                                   blank=True)
    free_ide = models.CharField(max_length=48,
                                blank=True)

    # Сообщество/открытость
    community_openness = models.DecimalField(max_digits=2,
                                             decimal_places=1)
    # Порог вхождения
    entry_threshold = models.IntegerField()

    power = models.DecimalField(max_digits=3,
                                decimal_places=1)
    analog_port = models.IntegerField()
    digital_port = models.IntegerField()

    width = models.DecimalField(max_digits=3,
                                decimal_places=1)
    length = models.DecimalField(max_digits=3,
                                 decimal_places=1)

    min_price = models.DecimalField(default=0.0,
                                    max_digits=6,
                                    decimal_places=2)
    max_price = models.DecimalField(max_digits=6,
                                    decimal_places=2)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('boards:board_detail',
                       args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name + ' ' + self.processor)
            super(Board, self).save(*args, **kwargs)

    class Meta:
        ordering = ('-name',)
