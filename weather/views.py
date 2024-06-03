from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import logging

logger = logging.getLogger(__name__)

def get_client_ip(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip:
        ip = ip.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class WeatherView(APIView):
    @method_decorator(cache_page(60 * 60 * 24))  # Cache por 24 horas
    def get(self, request, format=None):
        logger.info("Entrando a la función get de WeatherView")
        
        client_ip = get_client_ip(request)
        logger.info(f"IP del cliente: {client_ip}")

        # Para pruebas locales, usar una IP pública fija
        if client_ip.startswith("172.") or client_ip.startswith("192.168.") or client_ip.startswith("10."):
            client_ip = '8.8.8.8'  # Usar una IP pública conocida para pruebas
            logger.info(f"Usando IP pública fija para pruebas: {client_ip}")

        if not client_ip:
            logger.error("No se pudo obtener la IP del cliente")
            return Response({"error": "No se pudo obtener la IP del cliente"}, status=status.HTTP_400_BAD_REQUEST)

        # Usar la API de IPinfo para obtener la ubicación basada en la IP
        ipinfo_token = '5a8304e0458afd'
        ipinfo_url = f'https://ipinfo.io/{client_ip}/json?token={ipinfo_token}'
        ipinfo_response = requests.get(ipinfo_url)
        
        logger.info("Solicitud a IPinfo realizada")

        if ipinfo_response.status_code != 200:
            logger.error(f"Error en la solicitud a IPinfo: {ipinfo_response.status_code}")
            return Response({"error": "No se pudo obtener la ubicación basada en la IP"}, status=ipinfo_response.status_code)

        location_data = ipinfo_response.json()
        logger.info(f"Datos de ubicación recibidos: {location_data}")
        loc = location_data.get('loc')
        
        if not loc:
            logger.error("No se pudo determinar la ubicación")
            return Response({"error": "No se pudo determinar la ubicación"}, status=status.HTTP_400_BAD_REQUEST)
        
        lat, lon = loc.split(',')
        logger.info(f"Latitud: {lat}, Longitud: {lon}")

        # Usar la API de OpenWeatherMap para obtener el clima
        weather_api_key = 'eecfe41cfa293d349674239ee07e2d5f'
        weather_url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={weather_api_key}&units=metric'
        weather_response = requests.get(weather_url)
        
        logger.info("Solicitud a OpenWeatherMap realizada")

        if weather_response.status_code != 200:
            logger.error(f"Error en la solicitud a OpenWeatherMap: {weather_response.status_code}")
            return Response({"error": "No se pudo obtener la información del clima"}, status=weather_response.status_code)
        
        weather_data = weather_response.json()
        logger.info(f"Datos del clima recibidos: {weather_data}")

        weather_info = {
            'location': weather_data['name'],
            'temperature': weather_data['main']['temp'],
            'description': weather_data['weather'][0]['description']
        }
        
        return Response(weather_info, status=status.HTTP_200_OK)
