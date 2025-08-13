from django.shortcuts import render
from django.http import HttpResponse
import requests
from django.conf import settings
from datetime import datetime
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required

@login_required
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

    # Preparar lista de reseñas para la tabla
    reviews_list = []
    for key, item in posts.items():
        # Saltear entradas sin rating
        if 'rating' not in item:
            continue
            
        # Procesar timestamp
        ts = item.get('timestamp', '')
        formatted_date = ''
        parsed_date = None
        
        try:
            # Formato ISO (2023-10-27T10:30:00.000Z)
            if 'T' in ts and 'Z' in ts:
                parsed_date = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                # Convertir a naive para evitar problemas de timezone
                parsed_date = parsed_date.replace(tzinfo=None)
                formatted_date = parsed_date.strftime('%d/%m/%Y')
            # Formato dd/mm/yyyy con a. m./p. m.
            elif '/' in ts and ('a. m.' in ts or 'p. m.' in ts):
                # Cambiar "a. m." por "AM" y "p. m." por "PM" para parsing estándar
                ts_clean = ts.replace(' a. m.', ' AM').replace(' p. m.', ' PM')
                parsed_date = datetime.strptime(ts_clean, "%d/%m/%Y, %I:%M:%S %p")
                formatted_date = parsed_date.strftime('%d/%m/%Y')
            else:
                formatted_date = 'Fecha no válida'
                parsed_date = datetime.min  # Para ordenamiento (ya es naive)
        except Exception:
            formatted_date = 'Fecha no válida'
            parsed_date = datetime.min  # Para ordenamiento (ya es naive)
        
        reviews_list.append({
            'rating': item.get('rating', 0),
            'formatted_date': formatted_date,
            'parsed_date': parsed_date,
        })
    
    # Ordenar por fecha descendente (más reciente primero) y limitar a 15
    reviews_list.sort(key=lambda x: x['parsed_date'], reverse=True)
    reviews_list = reviews_list[:15]  # Limitar a 15 respuestas más recientes

    # Calcular métricas adicionales para mostrar en la tabla
    if reviews_list:
        recent_ratings = [r['rating'] for r in reviews_list]
        recent_avg_rating = round(sum(recent_ratings) / len(recent_ratings), 1)
        high_ratings_count = sum(1 for r in recent_ratings if r >= 4)
        recent_satisfaction = round((high_ratings_count / len(recent_ratings)) * 100, 1)
    else:
        recent_avg_rating = 0
        recent_satisfaction = 0

    # Generar datos para gráfico de líneas: Volumen Acumulado por Fecha
    # Crear lista de todas las reseñas con fechas válidas ordenadas cronológicamente
    all_reviews_for_chart = []
    for key, item in posts.items():
        if 'rating' not in item:
            continue
            
        ts = item.get('timestamp', '')
        parsed_date = None
        
        try:
            if 'T' in ts and 'Z' in ts:
                parsed_date = datetime.fromisoformat(ts.replace('Z', '+00:00')).replace(tzinfo=None)
            elif '/' in ts and ('a. m.' in ts or 'p. m.' in ts):
                ts_clean = ts.replace(' a. m.', ' AM').replace(' p. m.', ' PM')
                parsed_date = datetime.strptime(ts_clean, "%d/%m/%Y, %I:%M:%S %p")
        except Exception:
            continue
            
        if parsed_date:
            all_reviews_for_chart.append({
                'date': parsed_date,
                'formatted_date': parsed_date.strftime('%d/%m/%Y')
            })
    
    # Ordenar por fecha ascendente para acumulado
    all_reviews_for_chart.sort(key=lambda x: x['date'])
    
    # Crear datos acumulados: cada punto es el total hasta esa fecha
    chart_data = []
    for i, review in enumerate(all_reviews_for_chart):
        chart_data.append({
            'date': review['formatted_date'],
            'count': i + 1  # Acumulado: posición + 1
        })
    
    # Eliminar duplicados manteniendo el último count por fecha
    unique_chart_data = []
    seen_dates = {}
    for item in chart_data:
        seen_dates[item['date']] = item['count']
    
    for date, count in seen_dates.items():
        unique_chart_data.append({'date': date, 'count': count})
    
    # Ordenar por fecha para el gráfico
    unique_chart_data.sort(key=lambda x: datetime.strptime(x['date'], '%d/%m/%Y'))
    chart_data = unique_chart_data

        # Íconos SVG seguros (se enviarán como HTML)
    icons_svg = [
        mark_safe('<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z"></path></svg>'),
        mark_safe('<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path d="M10 15l-5.878 3.09 1.122-6.545L.488 6.91l6.561-.955L10 0l2.951 5.955 6.561.955-4.756 4.635 1.122 6.545z"></path></svg>'),
        mark_safe('<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path d="M2 10a8 8 0 1116 0A8 8 0 012 10zm8-3a1 1 0 100 2 1 1 0 000-2zm0 4a1 1 0 100 2 1 1 0 000-2zm0 4a1 1 0 100 2 1 1 0 000-2z"></path></svg>'),
        mark_safe('<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path d="M10 2a8 8 0 100 16 8 8 0 000-16zm3.93 6.36l-4.24 4.24a1 1 0 01-1.42 0l-2.12-2.12a1 1 0 111.42-1.42l1.41 1.41 3.53-3.53a1 1 0 111.42 1.42z"></path></svg>'),
    ]

    # Lista de indicadores para la plantilla
    indicators = [
        {
            'label': 'Número total de respuestas',
            'value': total_responses,
            'type': 'int',
            'icon': icons_svg[0],
        },
        {
            'label': 'Promedio de calificación',
            'value': average_rating,
            'type': 'float',
            'icon': icons_svg[1],
        },
        {
            'label': 'Reseñas este mes',
            'value': reviews_this_month,
            'type': 'int',
            'icon': icons_svg[2],
        },
        {
            'label': 'Clientes satisfechos',
            'value': percent_satisfied,
            'type': 'percent',
            'icon': icons_svg[3],
        },
    ]

    data = {
        'title': "Landing Page' Dashboard",
        'indicators': indicators,
        'reviews': reviews_list,
        'recent_avg_rating': recent_avg_rating,
        'recent_satisfaction': recent_satisfaction,
        'chart_data': chart_data,
        # variables planas por compatibilidad
        'total_responses': total_responses,
        'average_rating': average_rating,
        'reviews_this_month': reviews_this_month,
        'total_reviews': total_reviews,
        'percent_satisfied': percent_satisfied,
    }

    return render(request, 'dashboard/index.html', data)
