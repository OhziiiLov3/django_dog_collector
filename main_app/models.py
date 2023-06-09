from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date
# Import User Model 
from django.contrib.auth.models import User
# Create your models here.



MEALS = (
    ('B','Breakfast'),
    ('L','Lunch'),
    ('D','Dinner'),
)



class Toy(models.Model):
    name = models.CharField(max_length=25)
    color = models.CharField(max_length=20)


    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('toys_detail',kwargs={'pk': self.id})
    

class Dog(models.Model):
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    description = models.TextField(max_length=100)
    age = models.IntegerField()
    image = models.ImageField(null=True, blank=True)
    # # m:m relationship
    toys = models.ManyToManyField(Toy)
    # Add user fk
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('dogs_show',kwargs={'dog_id': self.id})
    
    def fed_for_today(self):
        return self.feeding_set.filter(date=date.today()).count() >= len(MEALS)


class Feeding(models.Model):
    date = models.DateField('feeding date')
    meal = models.CharField(max_length=1,choices=MEALS, default=MEALS[0][0])


    dog = models.ForeignKey(Dog, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.get_meal_display()} on {self.date}"
    
    # change the default to sort 
    class Meta:
        ordering = ['-date']



class Photo(models.Model):
    url = models.CharField(max_length=250)
    dog = models.ForeignKey(Dog, on_delete=models.CASCADE)

    def __str__(self):
        return f"Photo for dog_id: {self.dog_id} @{self.url}"

