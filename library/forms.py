from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Div, Layout, Row, Submit
from django import forms

from .models import Book, Author

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'url', 'collections']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["author"].queryset = Author.objects.order_by(
            "last_name"
        )  # Ensure ordering

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column("title", css_class="form-group col-md-8 mb-0"),
            ),
            Row(
                Column("author", css_class="form-group col-md-6 mb-0"),
                HTML("""
                     <div class="form-group col-md-6 mb-0 d-flex align-items-center">
                    <a href="#"
                        hx-get="{% url 'author_create' %}"
                        hx-target="#author-modal"
                        hx-swap="innerHTML"
                        class="text-primary ms-2">
                        <i class="fa fa-plus-circle"></i> Add Author
                    </a>
                    """),
            ),
            Row(
                Column("url", css_class="form-group col-md-6 mb-0"),
            ),

            HTML("<br>"),
            Row(
                HTML('<span class="form-group col-md-3 mb-0"></span>'),
                Submit(
                    "submit",
                    "Save",
                    css_class="form-group btn btn-primary col-md-1 mb-0",
                ),
                HTML('<span class="form-group col-md-3 mb-0"></span>'),
                HTML(
                    '<a href="javascript:javascript:history.go(-1)" class="form-group btn btn-danger col-md-1">Cancel</a>'
                ),
            ),
            Div(id="author-modal"),
        )

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = "__all__"
        exclude = ["first_name", "middle_name", "last_name", "user"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column("full_name", css_class="form-group col-md-6 mb-0"),
            ),

            HTML("<br>"),
            Row(
                HTML('<span class="form-group col-md-3 mb-0"></span>'),
                Submit(
                    "submit",
                    "Save",
                    css_class="form-group btn btn-primary col-md-1 mb-0",
                ),
                HTML('<span class="form-group col-md-3 mb-0"></span>'),
                HTML(
                    '<a href="javascript:javascript:history.go(-1)" class="form-group btn btn-danger col-md-1">Cancel</a>'
                ),
            ),
        )