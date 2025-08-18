from django.shortcuts import render
from django.http import HttpResponse

import requests
from django.conf import settings
from collections import Counter
from django.contrib.auth.decorators import permission_required, login_required

@login_required
@permission_required('dashboard.index_viewer', raise_exception=True)
def index(request):
    response = requests.get(settings.API_URL)  # URL de la API
    posts = response.json()  # Convertir la respuesta a JSON

    # Número total de respuestas
    total_responses = len(posts)

    # Preparar datos para los indicadores
    ratings = []
    names = []
    substantial_count = 0

    for key, review in posts.items():
        rating = review.get('rating')
        message = review.get('message', '')
        name = review.get('name', '')

        if rating is not None:
            ratings.append(rating)

        if len(message.strip()) > 10:
            substantial_count += 1

        if name:
            names.append(name)

    # 1. Promedio de calificación
    avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0

    # 2. Mensajes sustanciales vs triviales
    if total_responses > 0:
        substantial_percent = round((substantial_count / total_responses) * 100, 2)
    else:
        substantial_percent = 0

    # 3. Frecuencia de participación por usuario
    name_counts = Counter(names)
    repeated_users = sum(1 for count in name_counts.values() if count > 1)
    repeated_user_percent = round((repeated_users / len(name_counts)) * 100, 2) if name_counts else 0

    # 4. Reseñas con sus respectivos usuarios
    reviews = []
    for key, review in posts.items():
        reviews.append({
            'name': review.get('name', ''),
            'message': review.get('message', '')
        })

    # 5. Número de reseñas por cantidad de estrellas
    rating_counts = [0, 0, 0, 0, 0]  # índices 0 a 4 representan 1 a 5 estrellas
    for rating in ratings:
        if 1 <= rating <= 5:
            rating_counts[rating - 1] += 1

    data = {
        'title': "Landing Page' Dashboard",
        'total_responses': total_responses,
        'avg_rating': avg_rating,
        'substantial_percent': substantial_percent,
        'repeated_user_percent': repeated_user_percent,
        'reviews': reviews,
        'ratings_by_star': rating_counts,
    }

    return render(request, 'dashboard/index.html', data)
