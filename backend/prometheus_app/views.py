
# Create your views here.
from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .import prom

# Create your views here.
@require_http_methods(["GET"])
@csrf_exempt
class PrometheusView(View):
  def query_prometheus_data(request):
      if request.method == 'GET':

          pod = request.GET.get('pod')
          metric_name = request.GET.get('metric_name')
          start_time = request.GET.get('start_time')
          end_time = request.GET.get('end_time')      
          data = prom.query_range(metric_name, pod, start_time=start_time, end_time=end_time)

          if 'error' in data:
              return JsonResponse(data, status=404)
          else:
              # 根据需要格式化或转换data值
              return JsonResponse({'data': data}, status=200)
      else:
          return JsonResponse({'error': 'Invalid API request method.'}, status=400)