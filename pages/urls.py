from django.urls import path

from .views import (HomePageView, AboutPageView, BookListView, BookDetailView, \
    AuthorListView, AuthorDetailView, CollectionListView,
                    CollectionDetailView, SaveScrollPositionView, BookContentPartialView)

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("book_list/", BookListView.as_view(), name="book_list"),
    path("book_detail/<slug:slug>", BookDetailView.as_view(), name="book_detail"),
    path('books/<int:pk>/save-scroll/', SaveScrollPositionView.as_view(),
         name='save_scroll_position'),
    path('books/<int:pk>/content/', BookContentPartialView.as_view(),
         name='book_content_partial'),
    path("author_list/", AuthorListView.as_view(), name="author_list"),
    path("author_detail/<int:pk>", AuthorDetailView.as_view(),
         name="author_detail"),
    path("collection_list/", CollectionListView.as_view(), name="collection_list"),
    path("collection_detail/<int:pk>",
         CollectionDetailView.as_view(),
         name="collection_detail"),
    path("about/", AboutPageView.as_view(), name="about"),
]
