from django.shortcuts import render, redirect
from django.views.generic.edit import FormMixin
from .models import Board, Category
from django.views.generic import ListView, DetailView
from .forms import RequirementsForm


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
        if not req['processor_family']:
            print("*"*50)
        return redirect('boards:board_list')


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
