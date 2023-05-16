from django.shortcuts import render, get_object_or_404
from .models import Genre, Author, Book, BookInstance
from django.views import generic
from django.core.paginator import Paginator
from django.db.models import Q


# Class based
class BookListView(generic.ListView):
    model = Book
    # patys galite nustatyti šablonui kintamojo vardą
    context_object_name = 'my_book_list'
    # gauti sąrašą 3 knygų su žodžiu pavadinime 'The'
  #  queryset = Book.objects.filter(title__icontains='The')[:3]
    # šitą jau panaudojome. Neįsivaizduojate, kokį default kelią sukuria :)
    paginate_by = 2
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
    book_count = Book.objects.all().count()
    book_instance_count = BookInstance.objects.all().count()
    aveilable_books_count = BookInstance.objects.filter(book_status__exact='a').count()

    author_count = Author.objects.all().count()

    context = {
        'books': book_count,
        'book_instances': book_instance_count,
        'authors': author_count,
        'available': aveilable_books_count
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
    paprasta paieška. query ima informaciją iš paieškos laukelio,
    search_results prafiltruoja pagal įvestą tekstą knygų pavadinimus ir aprašymus.
    Icontains nuo contains skiriasi tuo, kad icontains ignoruoja ar raidės
    didžiosios/mažosios.
    """
    query = request.GET.get('query')
    search_results = Book.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) |
                                         Q(author__first_name__icontains=query))
    return render(request, 'search.html', {'books': search_results, 'query': query})


from django.contrib.auth.decorators import login_required

@login_required
def profile(request):
    return render(request, 'profile.html')
