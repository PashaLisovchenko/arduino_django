from decimal import Decimal
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from django.views.generic.edit import FormMixin
from .models import Board, Category
from django.views.generic import ListView, DetailView
from .forms import RequirementsForm
from django.db.models import F, DecimalField, ExpressionWrapper, Value


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
    query_response = []

    if req['processor_family']:
        boards = boards.filter(processor__family_id=req['processor_family'])
        query_response.append('processor_family')
    if req['language']:
        boards = boards.filter(programming_languages__id = req['language'])
        query_response.append('language')
    if req['form']:
        boards = get_board_form(req, boards)
        query_response.append('form')

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
        # todo узнать искать среди всех, или только по уровню знаний?
        ol = object_list.all()
        # после сужения плат нету, ищем лучшие результаты по категориям отдельно
        if 'processor_family' in query_response:
            boards_processor = ol.filter(processor__family_id=req['processor_family'])
            boards_processor = get_distance_boards(boards_processor, analog=req['analog'],
                                                   digit=req['digit'], voltage=req['voltage'], price=req['price'])
        else:
            boards_processor = None
        if 'language' in query_response:
            boards_language = ol.filter(programming_languages__id=req['language'])
            boards_language = get_distance_boards(boards_language, analog=req['analog'],
                                                  digit=req['digit'], voltage=req['voltage'], price=req['price'])
        else:
            boards_language = None
        if 'form' in query_response:
            boards_form = get_board_form(req, ol)
            boards_form = get_distance_boards(boards_form, analog=req['analog'], digit=req['digit'],
                                              voltage=req['voltage'], price=req['price'])
        else:
            boards_form = None
        return render(request, 'boards/list.html',
                      context={'boards_form': boards_form, 'boards_processor': boards_processor,
                               'boards_language': boards_language, 'form': form_class, 'category': category,
                               'categories': categories, 'rec': True
                               })


def get_distance_boards(boards, analog=None, digit=None, voltage=None, price=None):
    if not analog and not digit and not voltage and not price:
        return boards[:4]
    else:
        if analog:
            boards = boards.annotate(d_analog=ExpressionWrapper(
                    (int(analog) - F('analog_port')) * (int(analog) - F('analog_port')),
                    output_field=DecimalField()))
        else:
            boards = boards.annotate(d_analog=ExpressionWrapper(Value(0), output_field=DecimalField()))
        if digit:
            boards = boards.annotate(d_digit=ExpressionWrapper(
                (int(digit) - F('digital_port')) * (int(digit) - F('digital_port')),
                output_field=DecimalField()))
        else:
            boards = boards.annotate(d_digit=ExpressionWrapper(Value(0), output_field=DecimalField()))
        if voltage:
            boards = boards.annotate(d_voltage=ExpressionWrapper(
                (Decimal(voltage) - F('power')) * (Decimal(voltage) - F('power')),
                output_field=DecimalField()))
        else:
            boards = boards.annotate(d_voltage=ExpressionWrapper(Value(0), output_field=DecimalField()))
        if price:
            boards = boards.annotate(d_price=ExpressionWrapper(
                (Decimal(price) - F('max_price')) * (Decimal(price) - F('max_price')),
                output_field=DecimalField()))
        else:
            boards = boards.annotate(d_price=ExpressionWrapper(Value(0), output_field=DecimalField()))

        boards = boards.annotate(expires=ExpressionWrapper(
            F('d_analog') + F('d_digit') + F('d_voltage') + F('d_price'),
            output_field=DecimalField())).order_by('expires')
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
