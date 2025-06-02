from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import random
from .models import User, Score
from constants import SAMPLE_TEXTS

def index(request):
    return render(request, 'index.html', {'title': 'Home'})

def register_page(request):
    return render(request, 'register.html', {'title': 'Register'})

def login_page(request):
    return render(request, 'login.html', {'title': 'Login'})

def test_page(request):
    return render(request, 'test.html', {'title': 'Typing Test'})

def get_text(request):
    text = random.choice(SAMPLE_TEXTS)
    return JsonResponse({'text': text})

@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = request.POST
        if User.objects.filter(email=data['email']).exists():
            return JsonResponse({'error': 'Email already registered'}, status=400)
        
        user = User.objects.create(
            username=data['email'],
            email=data['email'],
            name=data['name'],
            password=make_password(data['password'])
        )
        
        return JsonResponse({
            'id': str(user.id),
            'name': user.name,
            'email': user.email
        })
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = request.POST
        user = authenticate(request, username=data['email'], password=data['password'])
        
        if user is not None:
            login(request, user)
            return JsonResponse({
                'id': str(user.id),
                'name': user.name,
                'email': user.email
            })
        return JsonResponse({'error': 'Invalid credentials'}, status=401)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@login_required
def save_score(request):
    if request.method == 'POST':
        data = request.POST
        score = Score.objects.create(
            user=request.user,
            wpm=data['wpm'],
            accuracy=data['accuracy'],
            mistakes=data['mistakes'],
            duration=data['duration']
        )
        return JsonResponse({'message': 'Score saved successfully'})
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def get_scores(request):
    scores = Score.objects.filter(user=request.user).order_by('-wpm')[:10]
    return JsonResponse([{
        'wpm': score.wpm,
        'accuracy': score.accuracy,
        'mistakes': score.mistakes,
        'duration': score.duration,
        'date': score.date.isoformat()
    } for score in scores], safe=False) 