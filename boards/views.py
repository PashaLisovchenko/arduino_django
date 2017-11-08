from django.shortcuts import render
from .models import Board, Category
from django.views.generic import ListView, DetailView
from .forms import RequirementsForm


class BoardList(ListView):
    template_name = 'boards/list.html'
    model = Board
    paginate_by = 9
    context_object_name = 'boards'

    def get_context_data(self, **kwargs):
        context = super(BoardList, self).get_context_data(**kwargs)
        category = None
        form = RequirementsForm()
        context['form'] = form
        categories = Category.objects.all()
        context['category'] = category
        context['categories'] = categories
        return context


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
