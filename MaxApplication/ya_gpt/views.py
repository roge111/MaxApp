from django.shortcuts import render



from managers.ManagerGPT import ManagerYandexGPT
# Create your views here.


def yandex_gpt(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input', '')
        if user_input:
            manager = ManagerYandexGPT()
            response, error = manager.ask_yandex_gpt(user_input)
            if not error:
                # Парсим ответ от GPT
                try:
                    parsed_response = manager.parser_response_gpt(response)
                    return render(request, 'ya_gpt/yandex_gpt.html', {
                        'response': parsed_response,
                        'user_input': user_input
                    })
                except Exception as e:
                    return render(request, 'ya_gpt/yandex_gpt.html', {
                        'error': f"Ошибка при парсинге ответа: {e}"
                    })
            else:
                return render(request, 'ya_gpt/yandex_gpt.html', {
                    'error': response
                })
        else:
            return render(request, 'ya_gpt/yandex_gpt.html', {
                'error': 'Пожалуйста, введите текст запроса.'
            })
    return render(request, 'ya_gpt/yandex_gpt.html')


