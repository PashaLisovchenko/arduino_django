from _decimal import Decimal
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


def get_distance_boards(request, boards, analog=None, digit=None, voltage=None, price=None):
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
        know_level = 2
        if req['knowledge_level'] == 'professional':
            # boards = платы по уровню знаний
            boards = Board.objects.annotate(knowledge_level=F('community_openness') + F('entry_threshold')) \
                .filter(knowledge_level__lte=know_level)
        else:
            # boards = платы по уровню знаний
            boards = Board.objects.annotate(knowledge_level=F('community_openness')+F('entry_threshold')) \
                .filter(knowledge_level__gt=know_level)
        # kl = boards

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
                    return render(self.request, 'boards/recommendations.html', context={'boards': boards})
                elif len(boards) > 1:
                    boards = get_distance_boards(self.request, boards, analog=req['analog'], digit=req['digit'],
                                                 voltage=req['voltage'], price=req['price'])
                    return render(self.request, 'boards/recommendations.html', context={'boards': boards})
            else:
                kl = Board.objects.all()
                # после сужения плат нету, ищем лучшие результаты по категориям отдельно
                boards_form = get_board_form(req, kl)
                boards_processor = kl.filter(processor__family_id=req['processor_family'])
                boards_language = kl.filter(programming_languages__id=req['language'])

                boards_form = get_distance_boards(self.request, boards_form, analog=req['analog'], digit=req['digit'],
                                                  voltage=req['voltage'], price=req['price'])
                boards_processor = get_distance_boards(self.request, boards_processor, analog=req['analog'],
                                                       digit=req['digit'], voltage=req['voltage'], price=req['price'])
                boards_language = get_distance_boards(self.request, boards_language, analog=req['analog'],
                                                      digit=req['digit'], voltage=req['voltage'], price=req['price'])
                return render(self.request, 'boards/recommendations.html',
                              context={'boards_form': boards_form,
                                       'boards_processor': boards_processor,
                                       'boards_language': boards_language
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
                    return render(self.request, 'boards/recommendations.html', context={'boards': boards})
                elif len(boards) > 1:
                    boards = get_distance_boards(self.request, boards, analog=req['analog'], digit=req['digit'],
                                                 voltage=req['voltage'], price=req['price'])
                    return render(self.request, 'boards/recommendations.html', context={'boards': boards})
            else:
                kl = Board.objects.all()
                # после сужения плат нету, ищем лучшие результаты по категориям отдельно
                boards_processor = kl.filter(processor__family_id=req['processor_family'])
                boards_language = kl.filter(programming_languages__id=req['language'])

                boards_processor = get_distance_boards(self.request, boards_processor, analog=req['analog'],
                                                       digit=req['digit'], voltage=req['voltage'], price=req['price'])
                boards_language = get_distance_boards(self.request, boards_language, analog=req['analog'],
                                                      digit=req['digit'], voltage=req['voltage'], price=req['price'])
                return render(self.request, 'boards/recommendations.html',
                              context={'boards_processor': boards_processor,
                                       'boards_language': boards_language
                                       })
        elif req['processor_family'] and req['form']:
            boards_form = get_board_form(req, boards)
            boards = boards_form.filter(processor__family_id=req['processor_family'])

            print("['processor_family'] and ['form']")
            print(boards)

            if boards:
                # после сужения, платы есть
                if len(boards) == 1:
                    # вывод платы если она одна
                    return render(self.request, 'boards/recommendations.html', context={'boards': boards})
                elif len(boards) > 1:
                    boards = get_distance_boards(self.request, boards, analog=req['analog'], digit=req['digit'],
                                                 voltage=req['voltage'], price=req['price'])
                    return render(self.request, 'boards/recommendations.html', context={'boards': boards})
            else:
                kl = Board.objects.all()
                # после сужения плат нету, ищем лучшие результаты по категориям отдельно
                boards_form = get_board_form(req, kl)
                boards_processor = kl.filter(processor__family_id=req['processor_family'])

                boards_form = get_distance_boards(self.request, boards_form, analog=req['analog'], digit=req['digit'],
                                                  voltage=req['voltage'], price=req['price'])
                boards_processor = get_distance_boards(self.request, boards_processor, analog=req['analog'],
                                                       digit=req['digit'], voltage=req['voltage'], price=req['price'])
                return render(self.request, 'boards/recommendations.html',
                              context={'boards_form': boards_form,
                                       'boards_processor': boards_processor
                                       })
        elif req['language'] and req['form']:
            boards_form = get_board_form(req, boards)
            boards = boards_form.filter(programming_languages__id=req['language'])

            print("['language'] and ['form']")
            print(boards)
            if boards:
                # после сужения, платы есть
                if len(boards) == 1:
                    # вывод платы если она одна
                    return render(self.request, 'boards/recommendations.html', context={'boards': boards})
                elif len(boards) > 1:
                    boards = get_distance_boards(self.request, boards, analog=req['analog'], digit=req['digit'],
                                                 voltage=req['voltage'], price=req['price'])
                    return render(self.request, 'boards/recommendations.html', context={'boards': boards})
            else:
                kl = Board.objects.all()
                # после сужения плат нету, ищем лучшие результаты по категориям отдельно
                boards_form = get_board_form(req, kl)
                boards_language = kl.filter(programming_languages__id=req['language'])

                boards_form = get_distance_boards(self.request, boards_form, analog=req['analog'], digit=req['digit'],
                                                  voltage=req['voltage'], price=req['price'])
                boards_language = get_distance_boards(self.request, boards_language, analog=req['analog'],
                                                      digit=req['digit'], voltage=req['voltage'], price=req['price'])
                return render(self.request, 'boards/recommendations.html',
                              context={'boards_form': boards_form,
                                       'boards_language': boards_language
                                       })

        elif req['processor_family']:
            boards = boards.filter(processor__family_id=req['processor_family'])

            print("['processor_family']")
            print(boards)
            if boards:
                # после сужения, платы есть
                if len(boards) == 1:
                    # вывод платы если она одна
                    return render(self.request, 'boards/recommendations.html', context={'boards': boards})
                elif len(boards) > 1:
                    boards = get_distance_boards(self.request, boards, analog=req['analog'], digit=req['digit'],
                                                 voltage=req['voltage'], price=req['price'])
                    return render(self.request, 'boards/recommendations.html', context={'boards': boards})
            else:
                # после сужения плат нету, ищем лучшие результаты по категориям отдельно
                kl = Board.objects.all()
                boards_processor = kl.filter(processor__family_id=req['processor_family'])

                boards_processor = get_distance_boards(self.request, boards_processor, analog=req['analog'],
                                                       digit=req['digit'], voltage=req['voltage'], price=req['price'])
                return render(self.request, 'boards/recommendations.html',
                              context={'boards_processor': boards_processor})
        elif req['language']:
            boards = boards.filter(programming_languages__id=req['language'])

            print("['language']")
            print(boards)
            if boards:
                # после сужения, платы есть
                if len(boards) == 1:
                    # вывод платы если она одна
                    return render(self.request, 'boards/recommendations.html', context={'boards': boards})
                elif len(boards) > 1:
                    boards = get_distance_boards(self.request, boards, analog=req['analog'], digit=req['digit'],
                                                 voltage=req['voltage'], price=req['price'])
                    return render(self.request, 'boards/recommendations.html', context={'boards': boards})
            else:
                kl = Board.objects.all()
                # после сужения плат нету, ищем лучшие результаты по категориям отдельно
                boards_language = kl.filter(programming_languages__id=req['language'])
                boards_language = get_distance_boards(self.request, boards_language, analog=req['analog'],
                                                      digit=req['digit'], voltage=req['voltage'], price=req['price'])
                return render(self.request, 'boards/recommendations.html',
                              context={'boards_language': boards_language})
        elif req['form']:
            boards = get_board_form(req, boards)
            print("['form']")
            print(boards)
            if boards:
                # после сужения, платы есть
                if len(boards) == 1:
                    # вывод платы если она одна
                    return render(self.request, 'boards/recommendations.html', context={'boards': boards})
                elif len(boards) > 1:
                    boards = get_distance_boards(self.request, boards, analog=req['analog'], digit=req['digit'],
                                                 voltage=req['voltage'], price=req['price'])
                    return render(self.request, 'boards/recommendations.html', context={'boards': boards})
            else:
                kl = Board.objects.all()
                # после сужения плат нету, ищем лучшие результаты по категориям отдельно
                boards_form = get_board_form(req, kl)

                boards_form = get_distance_boards(self.request, boards_form, analog=req['analog'], digit=req['digit'],
                                                  voltage=req['voltage'], price=req['price'])
                return render(self.request, 'boards/recommendations.html',
                              context={'boards_form': boards_form})
        else:
            # Если пользователь невводил ни каких жестких параметров
            # То мы получаем все платы по уровню знаний
            boards = get_distance_boards(self.request, kl, analog=req['analog'], digit=req['digit'],
                                         voltage=req['voltage'], price=req['price'])
            return render(self.request, 'boards/recommendations.html', context={'boards': boards})


class BoardListByCategory(DetailView):
    template_name = 'boards/list.html'
    model = Category
    context_object_name = 'category'
    slug_url_kwarg = 'category_slug'

    def get_context_data(self, **kwargs):
        context = super(BoardListByCategory, self).get_context_data(**kwargs)
        categories = Category.objects.all()
        form = RequirementsForm()
        context['form'] = form
        boards = Board.objects.filter(category=context['category'])
        context['categories'] = categories
        context['boards'] = boards
        return context


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
