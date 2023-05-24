# Create your views here.
from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .import trace1

# 忽略 CSRF 保护
@csrf_exempt
# 限制 HTTP 方法为 GET
@require_http_methods(['GET'])

class traceView(View):
  def query_trace_data(request):   
    if request.method == 'GET':
      mode = request.GET.get('mode')
      # 如果有 mode 那么就调用trace.query
      if mode:
        pod = request.GET.get('pod')
        size = request.GET.get('size')
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')
        label = request.GET.get('label')
        data = trace1.query(mode = mode, pod = pod, size = size,start_time = start_time,end_time = end_time,label = label)
      # 如果没有，那么判断有没有 key
      else:
        key = request.GET.get('key')
        if key:
          value = request.GET.get('value')
          data = trace1.data_search(key = key,value = value)
        else:
          value = request.GET.get('value')
          data = trace1.full_text_search(value = value)
      if not data:
          return JsonResponse({'error': 'No data found.'}, status=404)
      else:
          # 根据需要格式化或转换data值
          return JsonResponse({'data': data}, status=200)
    else:
        return JsonResponse({'error': 'Invalid API request method.'}, status=400)
