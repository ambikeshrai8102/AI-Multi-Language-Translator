import json
import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum
from .models import Translation, FavoriteTranslation
from .translation_engine import claude_translate, LANGUAGE_CODES, LANGUAGE_FLAGS

# ─── Language Data ────────────────────────────────────────────
LANGUAGES = [
    {'code': code, 'name': name, 'flag': LANGUAGE_FLAGS.get(code, '🌐')}
    for code, name in sorted(LANGUAGE_CODES.items(), key=lambda x: x[1])
]
LANGUAGES_JSON = json.dumps(LANGUAGES)

PHRASEBOOK_CATEGORIES = [
    {
        'name': 'Greetings & Basics', 'icon': '👋',
        'phrases': ['Hello', 'Good morning', 'Good afternoon', 'Good evening',
                    'Goodbye', 'See you later', 'How are you?', 'I am fine, thank you',
                    'Nice to meet you', 'Please', 'Thank you', 'You are welcome',
                    'Excuse me', 'I am sorry'],
    },
    {
        'name': 'Travel & Directions', 'icon': '✈️',
        'phrases': ['Where is the airport?', 'I need a taxi', 'How far is it?',
                    'Turn left', 'Turn right', 'Go straight ahead',
                    'I am lost', 'Can you help me?', 'How do I get to the hotel?',
                    'Where is the nearest metro station?'],
    },
    {
        'name': 'Food & Dining', 'icon': '🍽️',
        'phrases': ['I am hungry', 'A table for two, please', 'Can I see the menu?',
                    'I would like to order', 'The bill, please',
                    'I am vegetarian', 'I am allergic to nuts', 'This is delicious!',
                    'Can I have some water?', 'No sugar, please'],
    },
    {
        'name': 'Shopping', 'icon': '🛍️',
        'phrases': ['How much does this cost?', 'That is too expensive',
                    'Can you give me a discount?', 'I would like to buy this',
                    'Do you accept credit cards?', 'Where is the fitting room?',
                    'Do you have this in a larger size?', 'I am just looking'],
    },
    {
        'name': 'Emergency & Health', 'icon': '🚑',
        'phrases': ['Help!', 'Call the police!', 'Call an ambulance!',
                    'I need a doctor', 'I am sick', 'It hurts here',
                    'I have a fever', 'Where is the nearest hospital?',
                    'I have lost my passport', 'I need medicine'],
    },
    {
        'name': 'Numbers & Time', 'icon': '🕐',
        'phrases': ["What time is it?", "What is today's date?",
                    'Yesterday', 'Today', 'Tomorrow',
                    'In the morning', 'In the evening', 'At night',
                    'One', 'Two', 'Three', 'Ten', 'One hundred', 'One thousand'],
    },
]


def get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    return xff.split(',')[0] if xff else request.META.get('REMOTE_ADDR')


# ─── Auth Views ───────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('translator:index')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email    = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not username or not password1:
            messages.error(request, 'Username and password are required.')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif len(password1) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken. Please choose another.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            login(request, user)
            messages.success(request, f'Welcome, {username}! Account created successfully.')
            return redirect('translator:index')

    return render(request, 'translator/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('translator:index')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect(request.POST.get('next') or 'translator:index')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'translator/login.html', {'next': request.GET.get('next', '')})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('translator:login')


# ─── Main Pages ───────────────────────────────────────────────

@login_required(login_url='/login/')
def index(request):
    prefill_phrase = request.GET.get('phrase', '')
    recent_translations = Translation.objects.filter(user=request.user)[:6]
    stats = {
        'total_translations': Translation.objects.filter(user=request.user).count(),
        'total_characters': Translation.objects.filter(user=request.user).aggregate(t=Sum('character_count'))['t'] or 0,
        'languages_used': Translation.objects.filter(user=request.user).values('target_language').distinct().count(),
    }
    return render(request, 'translator/index.html', {
        'languages': LANGUAGES,
        'recent_translations': recent_translations,
        'stats': stats,
        'prefill_phrase': prefill_phrase,
    })


@csrf_exempt
@require_http_methods(["POST"])
def translate_text(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    try:
        data = json.loads(request.body)
        source_text = data.get('text', '').strip()
        source_lang = data.get('source_lang', 'auto')
        target_lang = data.get('target_lang', 'es')

        if not source_text:
            return JsonResponse({'error': 'No text provided'}, status=400)
        if len(source_text) > 5000:
            return JsonResponse({'error': 'Text too long (max 5000 characters)'}, status=400)

        result = claude_translate(source_text, source_lang, target_lang)
        translated_text = result['translated_text']
        detected_code   = result['detected_lang_code']
        detected_name   = result['detected_lang_name']
        target_lang_name = LANGUAGE_CODES.get(target_lang, target_lang)

        translation = Translation.objects.create(
            user=request.user,
            source_text=source_text,
            translated_text=translated_text,
            source_language=detected_code,
            target_language=target_lang,
            source_language_name=detected_name,
            target_language_name=target_lang_name,
            ip_address=get_client_ip(request),
        )

        return JsonResponse({
            'success': True,
            'translated_text': translated_text,
            'detected_language': detected_code,
            'detected_language_name': detected_name,
            'translation_id': translation.id,
        })

    except Exception as e:
        return JsonResponse({'error': f'Translation failed: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def batch_translate(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    try:
        data = json.loads(request.body)
        source_text  = data.get('text', '').strip()
        source_lang  = data.get('source_lang', 'auto')
        target_langs = data.get('target_langs', [])

        if not source_text:
            return JsonResponse({'error': 'No text provided'}, status=400)
        if not target_langs or len(target_langs) > 8:
            return JsonResponse({'error': 'Provide 1–8 target languages'}, status=400)

        results = []
        for lang in target_langs:
            try:
                r = claude_translate(source_text, source_lang, lang)
                results.append({
                    'lang_code': lang,
                    'lang_name': LANGUAGE_CODES.get(lang, lang),
                    'flag': LANGUAGE_FLAGS.get(lang, '🌐'),
                    'translated': r['translated_text'],
                })
            except Exception as e:
                results.append({'lang_code': lang, 'lang_name': lang, 'flag': '🌐', 'error': str(e)})

        return JsonResponse({'success': True, 'results': results})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required(login_url='/login/')
def history(request):
    query = request.GET.get('q', '')
    lang_filter = request.GET.get('lang', '')
    translations = Translation.objects.filter(user=request.user)
    if query:
        translations = translations.filter(source_text__icontains=query)
    if lang_filter:
        translations = translations.filter(target_language=lang_filter)
    translations = translations[:100]
    used_langs = Translation.objects.filter(user=request.user).values('target_language', 'target_language_name').distinct()
    return render(request, 'translator/history.html', {
        'translations': translations,
        'used_langs': used_langs,
        'query': query,
        'lang_filter': lang_filter,
    })


@login_required(login_url='/login/')
def favorites(request):
    favs = FavoriteTranslation.objects.filter(
        translation__user=request.user
    ).select_related('translation').all()
    return render(request, 'translator/favorites.html', {'favorites': favs})


@login_required(login_url='/login/')
def analytics(request):
    qs = Translation.objects.filter(user=request.user)
    top_targets = (qs.values('target_language', 'target_language_name')
                   .annotate(count=Count('id')).order_by('-count')[:10])
    top_sources = (qs.values('source_language', 'source_language_name')
                   .annotate(count=Count('id')).order_by('-count')[:10])
    for lang in top_targets:
        lang['flag'] = LANGUAGE_FLAGS.get(lang['target_language'], '🌐')
    for lang in top_sources:
        lang['flag'] = LANGUAGE_FLAGS.get(lang['source_language'], '🌐')

    return render(request, 'translator/analytics.html', {
        'top_targets': list(top_targets),
        'top_sources': list(top_sources),
        'total': qs.count(),
        'total_chars': qs.aggregate(t=Sum('character_count'))['t'] or 0,
        'langs_count': qs.values('target_language').distinct().count(),
        'favs_count': FavoriteTranslation.objects.filter(translation__user=request.user).count(),
    })


@login_required(login_url='/login/')
def batch_page(request):
    return render(request, 'translator/batch.html', {
        'languages': LANGUAGES,
        'languages_json': LANGUAGES_JSON,
    })


@login_required(login_url='/login/')
def phrasebook(request):
    return render(request, 'translator/phrasebook.html', {
        'languages': LANGUAGES,
        'categories': PHRASEBOOK_CATEGORIES,
    })


@login_required(login_url='/login/')
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="translations.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'From', 'To', 'Source Text', 'Translation', 'Characters', 'Date'])
    for t in Translation.objects.filter(user=request.user):
        writer.writerow([t.id, t.source_language_name, t.target_language_name,
                         t.source_text, t.translated_text, t.character_count,
                         t.created_at.strftime('%Y-%m-%d %H:%M:%S')])
    return response


@csrf_exempt
@require_http_methods(["POST"])
def add_favorite(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    try:
        data = json.loads(request.body)
        translation = get_object_or_404(Translation, id=data.get('translation_id'), user=request.user)
        fav, created = FavoriteTranslation.objects.get_or_create(
            translation=translation, defaults={'label': data.get('label', '')}
        )
        return JsonResponse({'success': True, 'created': created, 'id': fav.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def delete_translation(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    translation = get_object_or_404(Translation, pk=pk, user=request.user)
    translation.delete()
    return JsonResponse({'success': True})


@csrf_exempt
@require_http_methods(["POST"])
def delete_favorite(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    fav = get_object_or_404(FavoriteTranslation, pk=pk, translation__user=request.user)
    fav.delete()
    return JsonResponse({'success': True})


def stats_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    qs = Translation.objects.filter(user=request.user)
    top_languages = (qs.values('target_language', 'target_language_name')
                     .annotate(count=Count('id')).order_by('-count')[:10])
    for lang in top_languages:
        lang['flag'] = LANGUAGE_FLAGS.get(lang['target_language'], '🌐')
    return JsonResponse({
        'total_translations': qs.count(),
        'total_characters': qs.aggregate(t=Sum('character_count'))['t'] or 0,
        'languages_used': qs.values('target_language').distinct().count(),
        'top_languages': list(top_languages),
    })