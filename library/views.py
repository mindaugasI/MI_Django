from django.shortcuts import render, get_object_or_404
from .models import Genre, Author, Book, BookInstance
from django.views import generic
from django.core.paginator import Paginator
from django.db.models import Q


# Class based
class BookListView(generic.ListView):
    model = Book
    # You can set a variable name for the template yourself
    context_object_name = 'my_book_list'
    # get a list of 3 books with the word 'The' in the title
  #  queryset = Book.objects.filter(title__icontains='The')[:3]
    paginate_by = 2
    # We have already used this one. You have no idea what default path it creates :)
    template_name = 'book_list.html'


# Ar galima ir taip:
# class BookListView(generic.ListView):
#     model = Book
#
#     def get_queryset(self):
#         return Book.objects.filter(title__icontains='The')[:3]

    # def get_context_data(self, **kwargs):
    #         context = super(BookListView, self).get_context_data(**kwargs)
    #         context['duomenys'] = 'eilutė iš lempos'
    #         return context


class BookDetailView(generic.DetailView):
    model = Book
    template_name = 'book_detail.html'


def index(request):
    # Count number of books and book instances
    book_count = Book.objects.all().count()
    book_instance_count = BookInstance.objects.all().count()
    # Count number of available books (with status 'a')
    available_books_count = BookInstance.objects.filter(book_status__exact='a').count()
    # Count number of authors
    author_count = Author.objects.all().count()

    # With the additional variable num_visits and load it into the context.
    visits_count = request.session.get('visits_count', 1)
    request.session['visits_count'] = visits_count + 1
    context = {
        'books': book_count,
        'book_instances': book_instance_count,
        'authors': author_count,
        'available': available_books_count,
        'visits': visits_count,
    }

    return render(request, "index.html", context)


# Function based
def authors(request):
    paginator = Paginator(Author.objects.all(), 2)
    page_number = request.GET.get('page')
    paged_authors = paginator.get_page(page_number)
    return render(request, 'authors.html', context={'authors': paged_authors})

def author(request, author_id):
    single_author = get_object_or_404(Author, pk=author_id)
    return render(request, 'author.html', {'author': single_author})

def search(request):
    """
    Simple search. query gets information from search box,
    search_results filters book titles and descriptions based on the entered text.
    Icontains differs from contains in that icontains ignores upper/lower case letters.
    """
    query = request.GET.get('query')
    search_results = Book.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) |
                                         Q(author__first_name__icontains=query) | Q(author__last_name__icontains=query))
    return render(request, 'search.html', {'books': search_results, 'query': query})


from django.contrib.auth.decorators import login_required

@login_required
def profile(request):
    return render(request, 'profile.html')
