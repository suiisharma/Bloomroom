from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Room, Topic, Message,User
from .forms import RoomForm, UserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import myRegistrationForm
from django.http import HttpResponse


def loginpage(request):
    if (request.user.is_authenticated):
        return redirect('home')

    if (request.method == 'POST'):
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            user = authenticate(request,email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Incorrect username or password')
        except:
            messages.error(request, 'User doesn\'t exist')

    return render(request, 'base/login.html')


def registerpage(request):
    if (request.method == 'POST'):
        form = myRegistrationForm(request.POST)
        if (form.is_valid()):
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Error occurred while registration')
    form = myRegistrationForm()
    return render(request, 'base/signup.html', {'form': form})


def logoutUser(request):
    if (request.user.is_authenticated):
        logout(request)
        return redirect('home')
    else:
        return redirect('login')


def home(request):
    q = request.GET.get('q') if request.GET.get('q') else ''
    rooms = Room.objects.filter(Q(topic__name__icontains=q) |
                                Q(name__icontains=q) |
                                Q(description__icontains=q)|
                                Q(host__username__icontains=q)
                                )

    room_count = Room.objects.count()
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q)
    )[0:10]
    topics = Topic.objects.all()[0:5]
    context = {'room_messages': room_messages, 'rooms': rooms,
               'topics': topics, 'rooms_count': room_count}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    comments = room.message_set.all()
    participants = room.participants.all()
    if (request.method == 'POST'):
        Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    context = {'room': room, 'comments': comments,
               'participants': participants}
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    roooms_count=Room.objects.count()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()[0:5]
    context = {'user': user, 'rooms': rooms,'rooms_count':roooms_count,
               'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if (request.method == 'POST'):
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('You are not allowed to update!')
    if (request.method == 'POST'):
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.topic = topic
        room.save()
        return redirect('home')
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('You are not allowed to Delete!')
    if (request.method == 'POST'):
        room.delete()
        return redirect('user-profile',pk=request.user.id)
    return render(request, 'base/delete_room.html', {'obj': room})


@login_required(login_url='login')
def deleteMessage(request, pk):
    msg = Message.objects.get(id=pk)
    if request.user != msg.user:
        return HttpResponse('You are not allowed to Delete!')
    if (request.method == 'POST'):
        msg.delete()
        return redirect('home')
    return render(request, 'base/delete_room.html', {'obj': msg})


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST,request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk=user.id)
    context = {'user': user, 'form': form}
    return render(request, 'base/update_user.html', context)


def topicsPage(request):
    q=request.GET.get('q')if request.GET.get('q')!=None else ''
    topics=Topic.objects.filter(name__icontains=q)
    room_count=Room.objects.count()
    return render(request, 'base/topics.html',{'topics':topics,'room_count':room_count})

def activityPage(request):
    room_messages=Message.objects.all()
    return render(request,'base/activity.html',{'room_messages':room_messages})