from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from .forms import BookForm, AuthorForm
from accounts.models import CustomUser
from .models import Book, Author, Collection, ReadingProgress
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.urls import reverse_lazy
from django.shortcuts import redirect, render



class HomePageView(TemplateView):
    template_name = "pages/home.html"


class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    template_name = "pages/book_create.html"
    context_object_name = "book"
    form_class = BookForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["add_update"] = "Save"
        return context

    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Form is invalid")
        print(form.errors)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("book_detail", kwargs={"slug": self.object.slug})


class BookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = "pages/book_list.html"
    context_object_name = "books"
    # queryset = Book.objects.all().order_by('title')
    def get_queryset(self):
        queryset = Book.objects.filter(user=self.request.user).order_by('title')
        return queryset




class BookDetailView(LoginRequiredMixin, DetailView):
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


class AuthorCreateView(CreateView):
    model = Author
    form_class = AuthorForm
    success_url = reverse_lazy("author_list")

    def get_template_names(self):
        """Dynamically choose the template based on the request type."""
        if self.request.headers.get("HX-Request"):
            return ["partials/author_create_partial.html"]  # Used for modal
        return ["pages/author_create.html"]  # Used for standard form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["add_update"] = "Save"
        return context

    def form_valid(self, form):
        """Handles successful form submission differently for HTMX and standard requests."""
        form.instance.user = self.request.user
        self.object = form.save()

        if self.request.headers.get("HX-Request"):
            # Return a JSON response for HTMX to handle dynamically
            return JsonResponse({"id": self.object.id, "full_name":
                self.object.full_name, "user":self.object.user.username})

        return redirect(self.get_success_url())

    def form_invalid(self, form):
        """Ensures errors return the correct HTML so the form re-renders properly."""
        return self.render_to_response(self.get_context_data(form=form))


class AuthorListView(LoginRequiredMixin, ListView):
    model = Author
    template_name = "pages/author_list.html"
    context_object_name = "authors"
    def get_queryset(self):
        queryset = Author.objects.filter(user=self.request.user).order_by(
            'last_name')
        return queryset


class AuthorDetailView(LoginRequiredMixin, DetailView):
    model = Author
    template_name = "pages/author_detail.html"
    context_object_name = "author"

    def get_context_data(self, **kwargs):
        context = super(AuthorDetailView, self).get_context_data(**kwargs)
        context['books'] = Book.objects.filter(author=self.object.pk).order_by(
            'title')
        return context


class CollectionListView(LoginRequiredMixin, ListView):
    model = Collection
    template_name = "pages/collection_list.html"
    context_object_name = "collections"
    def get_queryset(self):
        queryset = Collection.objects.filter(user=self.request.user).order_by('name')
        return queryset


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


