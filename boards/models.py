from django.db import models
from django.core.urlresolvers import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=48, db_index=True)
    slug = models.SlugField(max_length=48, unique=True, blank=True, db_index=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('boards:board_list_by_category',
                       args=[self.slug])


class FamilyProcessor(models.Model):
    name = models.CharField(max_length=48)

    def __str__(self):
        return self.name


class Processor(models.Model):
    name = models.CharField(max_length=48)
    family = models.ForeignKey(FamilyProcessor)

    def __str__(self):
        return self.name


class IDE(models.Model):
    name = models.CharField(max_length=48)

    def __str__(self):
        return self.name


class Languages(models.Model):
    name = models.CharField(max_length=48)

    def __str__(self):
        return self.name


class Board(models.Model):
    name = models.CharField(max_length=48)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    image = models.ImageField(upload_to='board_images/', blank=True)
    processor = models.ForeignKey(Processor, blank=True)
    category = models.ForeignKey(Category, blank=True, null=True)
    programming_languages = models.ManyToManyField(Languages, blank=True)
    free_ide = models.ManyToManyField(IDE, blank=True)
    # Сообщество/открытость
    community_openness = models.DecimalField(max_digits=2, decimal_places=1, db_index=True)
    # Порог вхождения
    entry_threshold = models.DecimalField(max_digits=2, decimal_places=1, db_index=True)
    power = models.DecimalField(max_digits=3, decimal_places=1)
    analog_port = models.IntegerField()
    digital_port = models.IntegerField()
    width = models.DecimalField(max_digits=3, decimal_places=1, db_index=True)
    length = models.DecimalField(max_digits=3, decimal_places=1, db_index=True)
    min_price = models.DecimalField(default=0.0, max_digits=6, decimal_places=2)
    max_price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('boards:board_detail',
                       args=[self.id, self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name + ' ' + self.processor.name)
            super(Board, self).save(*args, **kwargs)

    class Meta:
        ordering = ('id',)
        index_together = (('id', 'slug'),)
