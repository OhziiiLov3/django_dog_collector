from django.shortcuts import render, redirect
from .models import Dog, Toy, Photo
from .forms import FeedingForm
import uuid
import boto3
import os
from django.views.generic.edit import CreateView, UpdateView, DeleteView 
from django.views.generic.detail import  DetailView
from django.views.generic.list import ListView
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse_lazy

# Create your views here.


# Home View

def home(request):
    return render(request, 'home.html')


# About view
def about(request):
    return render(request,'about.html')

# Index Page-> View all Dogs 
# dummy data 
# dogs = [
#     {'name':'Zooty','breed':'English Bulldog', 'description':'chunky & fun', 'age':3},
#     {'name':'Zoey','breed':'French Bulldog', 'description':'goofy & happy', 'age':2},
#     {'name':'Zonks','breed':'English Bulldog', 'description':'spolied', 'age':1},
# ]

class DogCreate(CreateView):
    model = Dog
    fields = ['name','breed', 'description', 'age']
    success_url = '/dogs/{dog_id}'

    def form_valid(self,form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        messages.success(self.request, "Dog enter into the Collection")
        return HttpResponseRedirect('/dogs/'+ str(self.object.pk))
    
class DogUpdate(UpdateView):
    model = Dog
     # Let's disallow the renaming of a cat by excluding the name field!
    fields = ['breed', 'description', 'age']

class DogDelete(DeleteView):
    model = Dog
    success_url = '/dogs'


# View all DOGS--> GET all data from db 

def dogs_index(request):
    dogs = Dog.objects.all()
    return render(request,'dogs/index.html',{'dogs': dogs})

#  Show Dog Detials -> GET Dog by :id

def dogs_show(request, dog_id):
    dog = Dog.objects.get(id=dog_id)
# Get the toys the cat doesn't have...
  # First, create a list of the toy ids that the cat DOES have
    id_list = dog.toys.all().values_list('id')
    # now we can query for toys whose ids are not in the list 
    toys_dog_doesnt_have = Toy.objects.exclude(id__in=id_list)
    feeding_form = FeedingForm()
    return render(request, 'dogs/show.html',{
        'dog': dog, 'feeding_form': feeding_form,
        'toys': toys_dog_doesnt_have
    })

def add_feeding(request, dog_id):
    # create a ModelForm instance using the data in request.POST
    form = FeedingForm(request.POST)
    # validate form 
    if form.is_valid():
        # dont save the form to the db until vlaid 
        # has the dog_id assigned 
        new_feeding = form.save(commit=False)
        new_feeding.dog_id = dog_id
        new_feeding.save()
    return redirect('dogs_show',dog_id=dog_id)


class ToyList(ListView):
    model = Toy


class ToyDetail(DetailView):
    model = Toy

class ToyCreate(CreateView):
    model = Toy
    fields = '__all__'

class ToyUpdate(UpdateView):
    model = Toy
    fields = ['name', 'color']

class ToyDelete(DeleteView):
    model = Toy
    success_url = '/toys'



def assoc_toy(request,dog_id, toy_id):
    Dog.objects.get(id=dog_id).toys.add(toy_id)
    return redirect('dogs_show',dog_id=dog_id)


# remove toy 
def remove_toy(request,dog_id, toy_id):
    Dog.objects.get(id=dog_id).toys.remove(toy_id)
    return redirect('dogs_show',dog_id=dog_id)

# Add photo 
def add_photo(request,dog_id):
    # photo-file will be the name attribute on the input
    photo_file = request.FILES.get('photo-file',None)
    if photo_file:
        s3 = boto3.client('s3')
        # need a unique key for s3 / needs image file ext too
        key = uuid.uuid4().hex[6] + photo_file.name[photo_file.name.rfind('.'):]
        try:
            bucket = os.environ['S3_BUCKET']
            s3.upload_fileobj(photo_file,bucket,key)
            # build the full url string
            url = f"{os.environ['S3_BASE_URL']}{bucket}/{key}"
            Photo.objects.create(url=url, dog_id=dog_id)
        except Exception as e:
            print('An error occured uploading file to s3')
            print(e)
    return redirect('dogs_show', dog_id=dog_id)


