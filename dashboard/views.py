from django.shortcuts import render
from django.http import HttpResponse

import requests
from django.conf import settings
from collections import Counter
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    response = requests.get(settings.API_URL)  # URL de la API
    posts = response.json()  # Convertir la respuesta a JSON

    # Número total de respuestas
    total_responses = len(posts)

    # Preparar datos para los indicadores
    ratings = []
    names = []
    trivial_count = 0
    substantial_count = 0

    for key, review in posts.items():
        rating = review.get('rating')
        message = review.get('message', '')
        name = review.get('name', '')

        if rating is not None:
            ratings.append(rating)

        if len(message.strip()) < 10:
            trivial_count += 1
        else:
            substantial_count += 1

        if name:
            names.append(name)

    # 1. Promedio de calificación
    avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0

    # 2. Mensajes sustanciales vs triviales
    if total_responses > 0:
        substantial_percent = round((substantial_count / total_responses) * 100, 2)
        trivial_percent = round((trivial_count / total_responses) * 100, 2)
    else:
        substantial_percent = trivial_percent = 0

    # 3. Frecuencia de participación por usuario
    name_counts = Counter(names)
    repeated_users = sum(1 for count in name_counts.values() if count > 1)
    repeated_user_percent = round((repeated_users / len(name_counts)) * 100, 2) if name_counts else 0

    data = {
        'title': "Landing Page' Dashboard",
        'total_responses': total_responses,
        'avg_rating': avg_rating,
        'substantial_percent': substantial_percent,
        'trivial_percent': trivial_percent,
        'repeated_user_percent': repeated_user_percent,
    }

    return render(request, 'dashboard/index.html', data)
