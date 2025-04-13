from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.views import View
from .models import Book, Author, Collection, ReadingProgress
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import json


class HomePageView(TemplateView):
    template_name = "pages/home.html"


class BookListView(ListView):
    model = Book
    template_name = "pages/book_list.html"
    context_object_name = "books"
    queryset = Book.objects.all().order_by('title')


class BookDetailView(DetailView):
    model = Book
    template_name = "pages/book_detail.html"
    context_object_name = "book"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            progress = ReadingProgress.objects.filter(user=self.request.user, book=self.object).first()
            context['scroll_position'] = progress.scroll_position if progress else 0
        else:
            context['scroll_position'] = 0
        return context



class AuthorListView(ListView):
    model = Author
    template_name = "pages/author_list.html"
    context_object_name = "authors"
    queryset = Author.objects.all().order_by('last_name')


class AuthorDetailView(DetailView):
    model = Author
    template_name = "pages/author_detail.html"
    context_object_name = "author"

    def get_context_data(self, **kwargs):
        context = super(AuthorDetailView, self).get_context_data(**kwargs)
        context['books'] = Book.objects.filter(author=self.object.pk).order_by(
            'title')
        return context


class CollectionListView(ListView):
    model = Collection
    template_name = "pages/collection_list.html"
    context_object_name = "collections"
    queryset = Collection.objects.all().order_by('name')


class CollectionDetailView(DetailView):
    model = Collection
    template_name = "pages/collection_detail.html"
    context_object_name = "collection"

    def get_context_data(self, **kwargs):
        context = super(CollectionDetailView, self).get_context_data(**kwargs)
        context['books'] = Book.objects.filter(
            collections=self.object.pk).order_by('title')
        return context


class AboutPageView(TemplateView):
    template_name = "pages/about.html"



class SaveScrollPositionView(View):
    def post(self, request, pk):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Not authenticated'}, status=401)

        try:
            data = json.loads(request.body.decode('utf-8'))  # 💥 This decode is key
            scroll_position = int(data.get('scroll_position', 0))
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            return JsonResponse({'error': f'Invalid data: {str(e)}'}, status=400)

        book = get_object_or_404(Book, pk=pk)
        progress, _ = ReadingProgress.objects.get_or_create(user=request.user, book=book)
        progress.scroll_position = scroll_position
        progress.save()

        return JsonResponse({'status': 'ok'})


class BookContentPartialView(DetailView):
    model = Book
    template_name = "partials/book_content_partial.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


