from django.shortcuts import render, redirect
from django.http import JsonResponse
import google.generativeai as genai  # Import Gemini API

from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat
from django.utils import timezone

# Set up your Google Gemini API Key
GEMINI_API_KEY = "your-gemini-api"  # 🔴 Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)
models = genai.list_models()
for model in models:
    print(model.name)

# Function to get response from Google Gemini
def ask_gemini(message):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")  # Use Gemini Pro model
        response = model.generate_content(message)  # Send user message
        return response.text.strip()  # Return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Sorry, I couldn't process your request at the moment."

# Chatbot View
def chatbot(request):
    chats = Chat.objects.filter(user=request.user.id)

    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_gemini(message)

        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()
        return JsonResponse({'message': message, 'response': response})
    
    return render(request, 'chatbot.html', {'chats': chats})

# User Authentication Views (No change needed)
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                error_message = 'Error creating account'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = 'Passwords do not match'
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')
