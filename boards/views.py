from decimal import Decimal
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404
from django.shortcuts import render
from django.views.generic.edit import FormMixin
from .models import Board, Category
from django.views.generic import ListView, DetailView
from .forms import RequirementsForm
from django.db.models import F, DecimalField, ExpressionWrapper, Value, Func
from django.db.models import Max, Min


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
    if not req['language'] and not req['processor_family'] and not req['analog'] and not req['digit'] and \
            not req['voltage'] and not req['price'] and not req['form']:
        return render(request, 'boards/recommendations.html', {'boards': boards, 'category': category,
                                                               'categories': categories,
                                                               'rec': True})

    boards = get_distance_boards(kl, analog=req['analog'], digit=req['digit'],
                                 voltage=req['voltage'], price=req['price'])
    if req['processor_family']:
        boards = boards.filter(processor__family_id=req['processor_family'])
        query_response.append('processor_family')
    if req['language']:
        boards = boards.filter(programming_languages__id=req['language'])
        query_response.append('language')
    if req['form']:
        boards = get_board_form(req, boards)
        query_response.append('form')

    if boards:
        # после сужения, платы есть
        if len(boards) > 1:
            boards = boards[:4]
        return render(request, 'boards/recommendations.html', {'boards': boards, 'form': form_class,
                               'category': category, 'categories': categories, 'rec': True})
    else:
        # искать среди всех, тогда либо исключать найденные лучшие платы по другим критериям,
        # либо делать множества и определять пересечения и определять лучшие по нескольким критериям одновременно
        ol = object_list.all()
        boards = get_distance_boards(ol, analog=req['analog'], digit=req['digit'],
                                     voltage=req['voltage'], price=req['price'])
        # после сужения плат нету, ищем лучшие результаты по категориям отдельно
        if 'processor_family' in query_response:
            boards_processor = boards.filter(processor__family_id=req['processor_family'])
            # boards_processor = get_distance_boards(boards_processor, analog=req['analog'],
            #                                        digit=req['digit'], voltage=req['voltage'], price=req['price'])
        else:
            boards_processor = None
        if 'language' in query_response:
            boards_language = boards.filter(programming_languages__id=req['language'])
            if boards_processor:
                boards_language = boards_language.exclude(id=boards_processor[0].id)
            # boards_language = get_distance_boards(boards_language, analog=req['analog'],
            #                                       digit=req['digit'], voltage=req['voltage'], price=req['price'])
        else:
            boards_language = None
        if 'form' in query_response:
            boards_form = get_board_form(req, boards)
            if boards_processor:
                boards_form = boards_form.exclude(id=boards_processor[0].id)
            if boards_language:
                boards_form = boards_form.exclude(id=boards_language[0].id)
            # boards_form = get_distance_boards(boards_form, analog=req['analog'], digit=req['digit'],
            #                                   voltage=req['voltage'], price=req['price'])
        else:
            boards_form = None
        return render(request, 'boards/recommendations.html',
                      context={'boards_form': boards_form, 'boards_processor': boards_processor,
                               'boards_language': boards_language, 'form': form_class, 'category': category,
                               'categories': categories, 'rec': True
                               })


def get_distance_boards(boards, analog=None, digit=None, voltage=None, price=None):
    """
        closer_is_better(Func(F('name_field')-float(param),function='ABS'),
         'name_field', float(param)), output_field=DecimalField()))
    """
    if not analog and not digit and not voltage and not price:
        return boards
    else:
        query_line = []
        if analog:
            boards = boards.filter(analog_port__gte=int(analog)).annotate(d_analog=ExpressionWrapper(
                closer_is_better(Func(F('analog_port')-int(analog), function='ABS'), 'analog_port'), output_field=DecimalField()))
            query_line.append('analog')
        else:
            boards = boards.annotate(d_analog=ExpressionWrapper(Value(0), output_field=DecimalField()))
        if digit:
            boards = boards.filter(digital_port__gte=int(digit)).annotate(d_digit=ExpressionWrapper(
                closer_is_better(Func(F('digital_port')-int(digit), function='ABS'), 'digital_port'), output_field=DecimalField()))
            query_line.append('digit')
        else:
            boards = boards.annotate(d_digit=ExpressionWrapper(Value(0), output_field=DecimalField()))
        if voltage:
            boards = boards.filter(power__gte=float(voltage)).annotate(d_voltage=ExpressionWrapper(
                closer_is_better(Func(F('power') - float(voltage), function='ABS'), 'power'),
                output_field=DecimalField()))
            query_line.append('voltage')
        else:
            boards = boards.annotate(d_voltage=ExpressionWrapper(Value(0), output_field=DecimalField()))
        if price:
            # max - min / 2 = a
            # max - a = avg
            print(boards)
            boards = boards.annotate(avg=
                     (F('max_price') - ((F('max_price')-F('min_price'))/2))
                                     ).filter(avg__gt=0).annotate(d_price=ExpressionWrapper(
                less_is_better_price(F('avg')),
                output_field=DecimalField()))
            for b in boards:
                print(b.d_price)
            query_line.append('price')
        else:
            boards = boards.annotate(d_price=ExpressionWrapper(Value(0), output_field=DecimalField()))
        dict_weight = {'analog': 0.1, 'digit': 0.1, 'voltage': 0.1, 'price': 0.7}
        global_weight = 0
        for line in query_line:
            if line == 'analog':
                global_weight += 0.1
            if line == 'digit':
                global_weight += 0.1
            if line == 'voltage':
                global_weight += 0.1
            if line == 'price':
                global_weight += 0.7
        boards = boards.annotate(expires=ExpressionWrapper(
            (dict_weight['analog']*F('d_analog') + dict_weight['digit']*F('d_digit') +
             dict_weight['voltage']*F('d_voltage') + dict_weight['price']*F('d_price'))/global_weight,
            output_field=DecimalField())).order_by('-expires')
        print(boards)
        return boards


class BoardList(FormMixin, ListView):
    template_name = 'boards/list.html'
    model = Board
    form_class = RequirementsForm
    paginate_by = 12
    context_object_name = 'boards'

    def get(self, request, *args, **kwargs):
        if self.request.is_ajax():
            req = request.GET
            object_list = Board.objects.all()
            category = None
            categories = Category.objects.all()
            return get_board(req, object_list, self.request, self.form_class, category, categories)
        else:
            self.object_list = self.get_queryset()
            allow_empty = self.get_allow_empty()

            if not allow_empty:
                if self.get_paginate_by(self.object_list) is not None and hasattr(self.object_list, 'exists'):
                    is_empty = not self.object_list.exists()
                else:
                    is_empty = len(self.object_list) == 0
                if is_empty:
                    raise Http404(("Empty list and '%(class_name)s.allow_empty' is False.") % {
                        'class_name': self.__class__.__name__,
                    })
            context = self.get_context_data()
            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(BoardList, self).get_context_data(**kwargs)
        category = None
        categories = Category.objects.all()
        context['category'] = category
        context['categories'] = categories
        return context


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
        paginator = Paginator(object_list, 12)
        page = self.request.GET.get('page')
        try:
            boards = paginator.page(page)
        except PageNotAnInteger:
            boards = paginator.page(1)
        except EmptyPage:
            boards = paginator.page(paginator.num_pages)

        context['page'] = page
        context['categories'] = categories
        context['boards'] = boards
        return context

    def get(self, request, *args, **kwargs):
        if self.request.is_ajax():
            req = request.GET
            category = self.get_object()
            category_boards = Board.objects.filter(category=category)
            categories = Category.objects.all()
            return get_board(req, category_boards, self.request, self.form_class, category, categories)
        else:
            self.object = self.get_object()
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)


class BoardDetail(DetailView):
    template_name = 'boards/detail.html'
    model = Board
    context_object_name = 'board'
    pk_url_kwarg = 'pk'
    slug_url_kwarg = 'slug'


def more_is_better(obj, obj_field):
    max_value = Board.objects.all().aggregate(Max(str(obj_field)))
    min_value = Board.objects.all().aggregate(Min(str(obj_field)))
    sim = (obj - float(min_value[obj_field+'__min'])) / float(max_value[obj_field+'__max']-min_value[obj_field+'__min'])
    return sim


def less_is_better(obj, obj_field):
    max_value = Board.objects.all().aggregate(Max(str(obj_field)))
    min_value = Board.objects.all().aggregate(Min(str(obj_field)))
    sim = (float(max_value[obj_field+'__max'])-obj) / float(max_value[obj_field+'__max']-min_value[obj_field+'__min'])
    return sim


def less_is_better_price(obj):
    max_value = Board.objects.all().aggregate(Max('max_price'))
    min_value = Board.objects.all().aggregate(Min('min_price'))
    sim = (float(max_value['max_price__max'])-obj) / float(max_value['max_price__max']-min_value['min_price__min'])
    return sim


def closer_is_better_price(obj):
    max_value = Board.objects.all().aggregate(Max('max_price'))
    min_value = Board.objects.all().aggregate(Min('min_price'))
    sim = 1 - (obj / (float(max_value['max_price__max'] - min_value['min_price__min'])))
    return sim


def closer_is_better(obj, obj_field):
    max_value = Board.objects.all().aggregate(Max(str(obj_field)))
    min_value = Board.objects.all().aggregate(Min(str(obj_field)))
    sim = 1 - (obj / (float(max_value[obj_field+'__max'] - min_value[obj_field+'__min'])))
    return sim
