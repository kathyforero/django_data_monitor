from django.shortcuts import render
from django.http import HttpResponse
import requests
from django.conf import settings
from datetime import datetime

def index(request):
    response = requests.get(settings.API_URL)  # URL de la API
    posts = response.json()  # Convertir la respuesta a JSON

    # Número total de respuestas
    total_responses = len(posts)

    # Promedio de calificación general
    ratings = [item.get('rating', 0) for item in posts.values()]
    average_rating = round(sum(ratings) / len(ratings), 1) if ratings else 0

    # Reseñas este mes (agosto 2025)
    reviews_this_month = 0
    for item in posts.values():
        ts = item.get('timestamp', '')
        # Intenta parsear ambos formatos de fecha
        try:
            if "2025" in ts and ("08" in ts or "agosto" in ts or "08/" in ts):
                reviews_this_month += 1
            elif ts.startswith("2025-08"):
                reviews_this_month += 1
            else:
                # Intentar parsear formato "dd/mm/yyyy"
                dt = None
                try:
                    dt = datetime.strptime(ts, "%d/%m/%Y, %I:%M:%S %p.")
                except Exception:
                    pass
                if dt and dt.year == 2025 and dt.month == 8:
                    reviews_this_month += 1
        except Exception:
            continue

    # Volumen total de reseñas (igual a total_responses en este caso)
    total_reviews = total_responses

    # Porcentaje de reseñas con calificación >= 4
    satisfied_count = sum(1 for r in ratings if r >= 4)
    percent_satisfied = round((satisfied_count / total_responses) * 100, 1) if total_responses else 0

    data = {
        'title': "Landing Page' Dashboard",
        'total_responses': total_responses,
        'average_rating': average_rating,
        'reviews_this_month': reviews_this_month,
        'total_reviews': total_reviews,
        'percent_satisfied': percent_satisfied,
    }

    return render(request, 'dashboard/index.html', data)
