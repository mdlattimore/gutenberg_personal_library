from django.contrib import admin

from .models import Book, Author, Collection, ReadingProgress


class BookInline(admin.TabularInline):
    model = Book.collections.through  # ✅ Works for Many-to-Many Collection-Book
    extra = 0
    readonly_fields = ['book']


class AuthorBookInline(admin.TabularInline):
    model = Book  # ✅ Directly relates to Author
    fields = ['title', ]  # ✅ Only show title and collections
    readonly_fields = ['title']  # Optional: Make title read-only
    show_change_link = True
    extra = 0


class BookListAdmin(admin.ModelAdmin):
    model = Book
    list_display = ['title']
    ordering = ['title']
    filter_horizontal = ('collections',)  # ✅ Works in BookAdmin


class AuthorListAdmin(admin.ModelAdmin):
    model = Author
    list_display = ['last_name', 'first_name']
    ordering = ['last_name', 'first_name']
    inlines = [
        AuthorBookInline]  # ✅ Uses direct Book relation instead of Many-to-Many


class CollectionListAdmin(admin.ModelAdmin):
    list_display = ['name']
    inlines = [
        BookInline]  # ✅ Works because Book.collections.through links to Collection
    ordering = ['name']


class ReadingProgressAdmin(admin.ModelAdmin):
    model = ReadingProgress
    list_display = ['user', 'book', 'scroll_position']


admin.site.register(Book, BookListAdmin)
admin.site.register(Author, AuthorListAdmin)
admin.site.register(Collection, CollectionListAdmin)
admin.site.register(ReadingProgress, ReadingProgressAdmin)
