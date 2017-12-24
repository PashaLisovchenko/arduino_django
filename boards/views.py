from decimal import Decimal
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from django.views.generic.edit import FormMixin
from .models import Board, Category
from django.views.generic import ListView, DetailView
from .forms import RequirementsForm
from django.db.models import F, DecimalField, ExpressionWrapper


def get_board_form(req, boards):
    # Компактные < 30
    # Средние >= 30 && < 60
    # Крупные >= 60
    if req['form'] == 'small':
        boards_form = boards.annotate(area=F('width') * F('length')).filter(area__lt=30)
    elif req['form'] == 'medium':
        boards_form = boards.annotate(area=F('width') * F('length')).filter(area__gte=30) \
            .filter(area__lt=60)
    else:
        boards_form = boards.annotate(area=F('width') * F('length')).filter(area__gte=60)
    return boards_form


def get_board(req, object_list, request, form_class, category, categories):
    know_level = 2
    if req['knowledge_level'] == 'professional':
        # boards = платы по уровню знаний
        boards = object_list.annotate(knowledge_level=F('community_openness') + F('entry_threshold')) \
            .filter(knowledge_level__gte=know_level)
        # boards = object_list.all()
    else:
        # boards = платы по уровню знаний
        boards = object_list.annotate(knowledge_level=F('community_openness')+F('entry_threshold')) \
            .filter(knowledge_level__lt=know_level)
    kl = boards

    if req['processor_family'] and req['language'] and req['form']:
        boards_form = get_board_form(req, boards)
        boards = boards_form.filter(processor__family_id=req['processor_family'],
                                    programming_languages__id=req['language'])
        print("['processor_family'] and ['language'] and ['form']")
        print(boards)

        if boards:
            # после сужения, платы есть
            if len(boards) == 1:
                # вывод платы если она одна
                return render(request, 'boards/list.html', context={'boards': boards, 'form': form_class,
                                                                    'category': category, 'categories': categories,
                                                                    'rec': True})
            elif len(boards) > 1:
                boards = get_distance_boards(boards, analog=req['analog'], digit=req['digit'],
                                             voltage=req['voltage'], price=req['price'])
                return render(request, 'boards/list.html', context={'boards': boards, 'form': form_class,
                                                                    'category': category, 'categories': categories,
                                                                    'rec': True})
        else:
            kl = object_list.all()
            # после сужения плат нету, ищем лучшие результаты по категориям отдельно
            boards_form = get_board_form(req, kl)
            boards_processor = kl.filter(processor__family_id=req['processor_family'])
            boards_language = kl.filter(programming_languages__id=req['language'])

            boards_form = get_distance_boards(boards_form, analog=req['analog'], digit=req['digit'],
                                              voltage=req['voltage'], price=req['price'])
            boards_processor = get_distance_boards(boards_processor, analog=req['analog'],
                                                   digit=req['digit'], voltage=req['voltage'], price=req['price'])
            boards_language = get_distance_boards(boards_language, analog=req['analog'],
                                                  digit=req['digit'], voltage=req['voltage'], price=req['price'])
            return render(request, 'boards/list.html',
                          context={'boards_form': boards_form, 'boards_processor': boards_processor,
                                   'boards_language': boards_language, 'form': form_class, 'category': category,
                                   'categories': categories, 'rec': True
                                   })

    elif req['processor_family'] and req['language']:
        boards = boards.filter(processor__family_id=req['processor_family'],
                               programming_languages__id=req['language'])

        print("['processor_family'] and ['language']")
        print(boards)

        if boards:
            # после сужения, платы есть
            if len(boards) == 1:
                # вывод платы если она одна
                return render(request, 'boards/list.html', context={'boards': boards, 'form': form_class,
                                                                    'category': category, 'categories': categories,
                                                                    'rec': True})
            elif len(boards) > 1:
                boards = get_distance_boards(boards, analog=req['analog'], digit=req['digit'],
                                             voltage=req['voltage'], price=req['price'])
                return render(request, 'boards/list.html', context={'boards': boards, 'form': form_class,
                                                                    'category': category, 'categories': categories,
                                                                    'rec': True})
        else:
            kl = object_list.all()
            # после сужения плат нету, ищем лучшие результаты по категориям отдельно
            boards_processor = kl.filter(processor__family_id=req['processor_family'])
            boards_language = kl.filter(programming_languages__id=req['language'])

            boards_processor = get_distance_boards(boards_processor, analog=req['analog'],
                                                   digit=req['digit'], voltage=req['voltage'], price=req['price'])
            boards_language = get_distance_boards(boards_language, analog=req['analog'],
                                                  digit=req['digit'], voltage=req['voltage'], price=req['price'])
            return render(request, 'boards/list.html',
                          context={'boards_processor': boards_processor, 'boards_language': boards_language,
                                   'form': form_class, 'category': category, 'categories': categories,
                                   'rec': True})
    elif req['processor_family'] and req['form']:
        boards_form = get_board_form(req, boards)
        boards = boards_form.filter(processor__family_id=req['processor_family'])

        print("['processor_family'] and ['form']")
        print(boards)

        if boards:
            # после сужения, платы есть
            if len(boards) == 1:
                # вывод платы если она одна
                return render(request, 'boards/list.html', context={'boards': boards, 'form': form_class,
                                                                    'category': category, 'categories': categories,
                                                                    'rec': True})
            elif len(boards) > 1:
                boards = get_distance_boards(boards, analog=req['analog'], digit=req['digit'],
                                             voltage=req['voltage'], price=req['price'])
                return render(request, 'boards/list.html', context={'boards': boards, 'form': form_class,
                                                                    'category': category, 'categories': categories,
                                                                    'rec': True})
        else:
            kl = object_list.all()
            # после сужения плат нету, ищем лучшие результаты по категориям отдельно
            boards_form = get_board_form(req, kl)
            boards_processor = kl.filter(processor__family_id=req['processor_family'])

            boards_form = get_distance_boards(boards_form, analog=req['analog'], digit=req['digit'],
                                              voltage=req['voltage'], price=req['price'])
            boards_processor = get_distance_boards(boards_processor, analog=req['analog'],
                                                   digit=req['digit'], voltage=req['voltage'], price=req['price'])
            return render(request, 'boards/list.html',
                          context={'boards_form': boards_form, 'boards_processor': boards_processor,
                                   'form': form_class, 'category': category, 'categories': categories,
                                   'rec': True})
    elif req['language'] and req['form']:
        boards_form = get_board_form(req, boards)
        boards = boards_form.filter(programming_languages__id=req['language'])

        print("['language'] and ['form']")
        print(boards)
        if boards:
            # после сужения, платы есть
            if len(boards) == 1:
                # вывод платы если она одна
                return render(request, 'boards/list.html', context={'boards': boards, 'form': form_class,
                                                                    'category': category, 'categories': categories,
                                                                    'rec': True})
            elif len(boards) > 1:
                boards = get_distance_boards(boards, analog=req['analog'], digit=req['digit'],
                                             voltage=req['voltage'], price=req['price'])
                return render(request, 'boards/list.html', context={'boards': boards, 'form': form_class,
                                                                    'category': category, 'categories': categories,
                                                                    'rec': True})
        else:
            kl = object_list.all()
            # после сужения плат нету, ищем лучшие результаты по категориям отдельно
            boards_form = get_board_form(req, kl)
            boards_language = kl.filter(programming_languages__id=req['language'])

            boards_form = get_distance_boards(boards_form, analog=req['analog'], digit=req['digit'],
                                              voltage=req['voltage'], price=req['price'])
            boards_language = get_distance_boards(boards_language, analog=req['analog'],
                                                  digit=req['digit'], voltage=req['voltage'], price=req['price'])
            return render(request, 'boards/list.html',
                          context={'boards_form': boards_form, 'boards_language': boards_language,
                                   'form': form_class, 'category': category, 'categories': categories,
                                   'rec': True})

    elif req['processor_family']:
        boards = boards.filter(processor__family_id=req['processor_family'])

        print("['processor_family']")
        print(boards)
        if boards:
            # после сужения, платы есть
            if len(boards) == 1:
                # вывод платы если она одна
                return render(request, 'boards/list.html', context={'boards': boards, 'form': form_class,
                                                                    'category': category, 'categories': categories,
                                                                    'rec': True})
            elif len(boards) > 1:
                boards = get_distance_boards(boards, analog=req['analog'], digit=req['digit'],
                                             voltage=req['voltage'], price=req['price'])
                return render(request, 'boards/list.html', context={'boards': boards, 'form': form_class,
                                                                    'category': category, 'categories': categories,
                                                                    'rec': True})
        else:
            # после сужения плат нету, ищем лучшие результаты по категориям отдельно
            kl = object_list.all()
            boards_processor = kl.filter(processor__family_id=req['processor_family'])

            boards_processor = get_distance_boards(boards_processor, analog=req['analog'],
                                                   digit=req['digit'], voltage=req['voltage'], price=req['price'])
            return render(request, 'boards/list.html',
                          context={'boards_processor': boards_processor, 'form': form_class,
                                   'category': category, 'categories': categories,
                                   'rec': True})
    elif req['language']:
        boards = boards.filter(programming_languages__id=req['language'])

        print("['language']")
        print(boards)
        if boards:
            # после сужения, платы есть
            if len(boards) == 1:
                # вывод платы если она одна
                return render(request, 'boards/list.html', context={'boards': boards, 'form': form_class,
                                                                    'category': category, 'categories': categories,
                                                                    'rec': True})
            elif len(boards) > 1:
                boards = get_distance_boards(boards, analog=req['analog'], digit=req['digit'],
                                             voltage=req['voltage'], price=req['price'])
                return render(request, 'boards/list.html', context={'boards': boards, 'form': form_class,
                                                                    'category': category, 'categories': categories,
                                                                    'rec': True})
        else:
            kl = object_list.all()
            # после сужения плат нету, ищем лучшие результаты по категориям отдельно
            boards_language = kl.filter(programming_languages__id=req['language'])
            boards_language = get_distance_boards(boards_language, analog=req['analog'],
                                                  digit=req['digit'], voltage=req['voltage'], price=req['price'])
            return render(request, 'boards/list.html',
                          context={'boards_language': boards_language, 'form': form_class,
                                   'category': category, 'categories': categories, 'rec': True})
    elif req['form']:
        boards = get_board_form(req, boards)
        print("['form']")
        print(boards)
        if boards:
            # после сужения, платы есть
            if len(boards) == 1:
                # вывод платы если она одна
                return render(request, 'boards/list.html', context={'boards': boards, 'form': form_class,
                                                                    'category': category, 'categories': categories,
                                                                    'rec': True})
            elif len(boards) > 1:
                boards = get_distance_boards(boards, analog=req['analog'], digit=req['digit'],
                                             voltage=req['voltage'], price=req['price'])
                return render(request, 'boards/list.html', context={'boards': boards, 'form': form_class,
                                                                    'category': category, 'categories': categories,
                                                                    'rec': True})
        else:
            kl = object_list.all()
            # после сужения плат нету, ищем лучшие результаты по категориям отдельно
            boards_form = get_board_form(req, kl)

            boards_form = get_distance_boards(boards_form, analog=req['analog'], digit=req['digit'],
                                              voltage=req['voltage'], price=req['price'])
            return render(request, 'boards/list.html',
                          context={'boards_form': boards_form, 'form': form_class,
                                   'category': category, 'categories': categories,
                                   'rec': True})
    else:
        # Если пользователь невводил ни каких жестких параметров
        # То мы получаем все платы по уровню знаний
        boards = get_distance_boards(kl, analog=req['analog'], digit=req['digit'],
                                     voltage=req['voltage'], price=req['price'])
        return render(request, 'boards/list.html', context={'rec': True,
                                                            'boards': boards,
                                                            'form': form_class,
                                                            'category': category,
                                                            'categories': categories})


def get_distance_boards(boards, analog=None, digit=None, voltage=None, price=None):
    if analog and digit and voltage and price:
        boards = boards.annotate(expires=ExpressionWrapper(
            (int(analog) - F('analog_port')) * (int(analog) - F('analog_port')) +
            (int(digit) - F('digital_port')) * (int(digit) - F('digital_port')) +
            (Decimal(voltage) - F('power')) * (Decimal(voltage) - F('power')) +
            (Decimal(price) - F('max_price')) * (Decimal(price) - F('max_price')),
            output_field=DecimalField())).order_by('expires')
        # print(boards[0].expires)
        return boards[:4]
    elif analog and digit and voltage:
        boards = boards.annotate(expires=ExpressionWrapper(
            (int(analog) - F('analog_port')) * (int(analog) - F('analog_port')) +
            (int(digit) - F('digital_port')) * (int(digit) - F('digital_port')) +
            (Decimal(voltage) - F('power')) * (Decimal(voltage) - F('power')),
            output_field=DecimalField())).order_by('expires')
        return boards[:4]
    elif analog and digit and price:
        boards = boards.annotate(expires=ExpressionWrapper(
            (int(analog) - F('analog_port')) * (int(analog) - F('analog_port')) +
            (int(digit) - F('digital_port')) * (int(digit) - F('digital_port')) +
            (Decimal(price) - F('max_price')) * (Decimal(price) - F('max_price')),
            output_field=DecimalField())).order_by('expires')
        return boards[:4]
    elif analog and voltage and price:
        boards = boards.annotate(expires=ExpressionWrapper(
            (int(analog) - F('analog_port')) * (int(analog) - F('analog_port')) +
            (Decimal(voltage) - F('power')) * (Decimal(voltage) - F('power')) +
            (Decimal(price) - F('max_price')) * (Decimal(price) - F('max_price')),
            output_field=DecimalField())).order_by('expires')
        return boards[:4]
    elif digit and voltage and price:
        boards = boards.annotate(expires=ExpressionWrapper(
            (int(digit) - F('digital_port')) * (int(digit) - F('digital_port')) +
            (Decimal(voltage) - F('power')) * (Decimal(voltage) - F('power')) +
            (Decimal(price) - F('max_price')) * (Decimal(price) - F('max_price')),
            output_field=DecimalField())).order_by('expires')
        return boards[:4]
    elif analog and digit:
        boards = boards.annotate(expires=ExpressionWrapper(
            (int(analog) - F('analog_port')) * (int(analog) - F('analog_port')) +
            (int(digit) - F('digital_port')) * (int(digit) - F('digital_port')),
            output_field=DecimalField())).order_by('expires')
        return boards[:4]
    elif analog and voltage:
        boards = boards.annotate(expires=ExpressionWrapper(
            (int(analog) - F('analog_port')) * (int(analog) - F('analog_port')) +
            (Decimal(voltage) - F('power')) * (Decimal(voltage) - F('power')),
            output_field=DecimalField())).order_by('expires')
        return boards[:4]
    elif analog and price:
        boards = boards.annotate(expires=ExpressionWrapper(
            (int(analog) - F('analog_port')) * (int(analog) - F('analog_port')) +
            (Decimal(price) - F('max_price')) * (Decimal(price) - F('max_price')),
            output_field=DecimalField())).order_by('expires')
        return boards[:4]
    elif digit and voltage:
        boards = boards.annotate(expires=ExpressionWrapper(
            (int(digit) - F('digital_port')) * (int(digit) - F('digital_port')) +
            (Decimal(voltage) - F('power')) * (Decimal(voltage) - F('power')),
            output_field=DecimalField())).order_by('expires')
        return boards[:4]
    elif digit and price:
        boards = boards.annotate(expires=ExpressionWrapper(
            (int(digit) - F('digital_port')) * (int(digit) - F('digital_port')) +
            (Decimal(price) - F('max_price')) * (Decimal(price) - F('max_price')),
            output_field=DecimalField())).order_by('expires')
        return boards[:4]
    elif voltage and price:
        boards = boards.annotate(expires=ExpressionWrapper(
            (Decimal(voltage) - F('power')) * (Decimal(voltage) - F('power')) +
            (Decimal(price) - F('max_price')) * (Decimal(price) - F('max_price')),
            output_field=DecimalField())).order_by('expires')
        return boards[:4]
    elif analog:
        boards = boards.annotate(expires=ExpressionWrapper(
            (int(analog) - F('analog_port')) * (int(analog) - F('analog_port')),
            output_field=DecimalField())).order_by('expires')
        return boards[:4]
    elif digit:
        boards = boards.annotate(expires=ExpressionWrapper(
            (int(digit) - F('digital_port')) * (int(digit) - F('digital_port')),
            output_field=DecimalField())).order_by('expires')
        return boards[:4]
    elif voltage:
        boards = boards.annotate(expires=ExpressionWrapper(
            (Decimal(voltage) - F('power')) * (Decimal(voltage) - F('power')),
            output_field=DecimalField())).order_by('expires')
        return boards[:4]
    elif price:
        boards = boards.annotate(expires=ExpressionWrapper(
            (Decimal(price) - F('max_price')) * (Decimal(price) - F('max_price')),
            output_field=DecimalField())).order_by('expires')
        return boards[:4]
    else:
        return boards[:4]


class BoardList(FormMixin, ListView):
    template_name = 'boards/list.html'
    model = Board
    form_class = RequirementsForm
    paginate_by = 9
    context_object_name = 'boards'

    def get_context_data(self, **kwargs):
        context = super(BoardList, self).get_context_data(**kwargs)
        category = None
        categories = Category.objects.all()
        context['category'] = category
        context['categories'] = categories
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        print(self.request.POST)
        req = self.request.POST
        all_boards = Board.objects.all()
        category = None
        categories = Category.objects.all()
        return get_board(req, all_boards, self.request, self.form_class, category, categories)


class BoardListByCategory(FormMixin, DetailView):
    template_name = 'boards/list.html'
    model = Category
    form_class = RequirementsForm
    context_object_name = 'category'
    slug_url_kwarg = 'category_slug'

    def get_context_data(self, **kwargs):
        context = super(BoardListByCategory, self).get_context_data(**kwargs)
        categories = Category.objects.all()
        object_list = Board.objects.filter(category=context['category'])
        paginator = Paginator(object_list, 9)  # 3 posts in each page
        page = self.request.GET.get('page')
        try:
            boards = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer deliver the first page
            boards = paginator.page(1)
        except EmptyPage:
            # If page is out of range deliver last page of results
            boards = paginator.page(paginator.num_pages)

        context['page'] = page
        context['categories'] = categories
        context['boards'] = boards
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        print(self.request.POST)
        category = self.get_object()
        category_boards = Board.objects.filter(category=category)
        req = self.request.POST
        categories = Category.objects.all()
        return get_board(req, category_boards, self.request, self.form_class, category, categories)


class BoardDetail(DetailView):
    template_name = 'boards/detail.html'
    model = Board
    context_object_name = 'board'
    pk_url_kwarg = 'pk'
    slug_url_kwarg = 'slug'


# class Recommendation(ListView):
#     template_name = 'boards/recommendations.html'
#     model = Board
#     context_object_name = 'boards'
