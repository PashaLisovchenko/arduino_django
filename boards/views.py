from django.shortcuts import render, get_object_or_404
from .models import Board, Languages
# from django.views.generic import ListView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def boards_list(request):
    object_list_board = Board.objects.all()
    paginator = Paginator(object_list_board, 9)
    page = request.GET.get('page')
    try:
        boards = paginator.page(page)
    except PageNotAnInteger:
        boards = paginator.page(1)
    except EmptyPage:
        boards = paginator.page(paginator.num_pages)
    lang = Languages.objects.all()
    return render(request, 'boards/list.html', {'boards': boards,
                                                'lang': lang,
                                                'page': page})


def board_detail(request, board):
    board = get_object_or_404(Board, slug=board)
    return render(request, 'boards/detail.html', {'board': board})
