from django.shortcuts import render, redirect
from .models import Dog, Toy, Photo
from .forms import FeedingForm
import uuid
import boto3
import os
from django.views.generic.edit import CreateView, UpdateView, DeleteView 
from django.views.generic import ListView, DetailView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
# Import the login_required decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
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

class DogCreate(LoginRequiredMixin,CreateView):
    model = Dog
    fields = ['name','breed', 'description', 'age']
    success_url = '/dogs/{dog_id}'

    def form_valid(self,form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        messages.success(self.request, "Dog enter into the Collection")
        return HttpResponseRedirect('/dogs/'+ str(self.object.pk))
    #     # Assign the logged in user (self.request.user)
    #     form.instance.user = self.request.user  # form.instance is the cat
    # # Let the CreateView do its job as usual
    #     return super().form_valid(form)

    
class DogUpdate(LoginRequiredMixin,UpdateView):
    model = Dog
     # Let's disallow the renaming of a cat by excluding the name field!
    fields = ['breed', 'description', 'age']

class DogDelete(LoginRequiredMixin,DeleteView):
    model = Dog
    success_url = '/dogs'


# View all DOGS--> GET all data from db 
@login_required
def dogs_index(request):
      # This reads ALL cats, not just the logged in user's cats
    # dogs = Dog.objects.all()
    dogs = Dog.objects.filter(user=request.user)
    return render(request,'dogs/index.html',{'dogs': dogs})

#  Show Dog Detials -> GET Dog by :id
@login_required
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
@login_required
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


class ToyList(LoginRequiredMixin,ListView):
    model = Toy


class ToyDetail(LoginRequiredMixin,DetailView):
    model = Toy

class ToyCreate(LoginRequiredMixin,CreateView):
    model = Toy
    fields = '__all__'

class ToyUpdate(LoginRequiredMixin,UpdateView):
    model = Toy
    fields = ['name', 'color']

class ToyDelete(DeleteView):
    model = Toy
    success_url = '/toys'


@login_required
def assoc_toy(request,dog_id, toy_id):
    Dog.objects.get(id=dog_id).toys.add(toy_id)
    return redirect('dogs_show',dog_id=dog_id)


# remove toy 
@login_required
def remove_toy(request,dog_id, toy_id):
    Dog.objects.get(id=dog_id).toys.remove(toy_id)
    return redirect('dogs_show',dog_id=dog_id)

# Add photo 
@login_required
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

def login_view(request):
    render('registration/login.html')


def signup(request):
  error_message = ''
  if request.method == 'POST':
    # This is how to create a 'user' form object
    # that includes the data from the browser
    form = UserCreationForm(request.POST)
    if form.is_valid():
      # This will add the user to the database
      user = form.save()
      # This is how we log a user in via code
      login(request, user)
      return redirect('/')
    else:
      error_message = 'Invalid sign up - try again'
  # A bad POST or a GET request, so render signup.html with an empty form
  form = UserCreationForm()
  context = {'form': form, 'error_message': error_message}
  return render(request, 'registration/signup.html', context)

