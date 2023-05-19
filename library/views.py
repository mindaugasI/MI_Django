from django.shortcuts import render, get_object_or_404, redirect, reverse
from .models import Genre, Author, Book, BookInstance
from django.views import generic
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from .forms import BookReviewForm, UserUpdateForm, ProfileUpdateForm, UserBookCreateForm
from django.views.generic.edit import FormMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView



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


class BookDetailView(FormMixin, generic.DetailView):
    model = Book
    template_name = 'book_detail.html'
    form_class = BookReviewForm

    # we indicate where we will end up if the comment succeeds.
    def get_success_url(self):
        return reverse('book-detail', kwargs={'pk': self.object.book_id})

    # standard rewrite of the post method using FormMixin.
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    # here we specify that the book will be exactly the one under which we comment, and the user will be the one who is logged in.
    def form_valid(self, form):
        form.instance.book = self.object
        form.instance.reviewer = self.request.user
        form.save()
        return super(BookDetailView, self).form_valid(form)

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




#-------------------------cRud---------------------------------------
class LoanedBooksByUserListView(LoginRequiredMixin, ListView):
    model = BookInstance
    context_object_name = 'books'
    template_name = 'user_books.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(reader=self.request.user).order_by('due_back')


class BookByUserDetailView(LoginRequiredMixin, DetailView):
    model = BookInstance
    template_name = 'user_book.html'


class BookByUserCreateView(LoginRequiredMixin, CreateView):
    model = BookInstance
    #fields = ['book', 'due_back']
    success_url = "/library/mybooks/"
    template_name = 'user_book_form.html'
    form_class = UserBookCreateForm

    def form_valid(self, form):
        form.instance.reader = self.request.user
        return super().form_valid(form)

    def get_absolute_url(self):
        """Specifies the final address of a specific description"""
        return reverse('book-detail', args=[str(self.instance_id)])


class BookByUserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = BookInstance
    fields = ['book', 'due_back']
    success_url = "/library/mybooks/"
    template_name = 'user_book_form.html'

    def form_valid(self, form):
        form.instance.reader = self.request.user
        return super().form_valid(form)

    def test_func(self):
        book = self.get_object()
        return self.request.user == book.reader


class BookByUserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = BookInstance
    success_url = "/library/mybooks/"
    template_name = 'user_book_delete.html'

    def test_func(self):
        book = self.get_object()
        return self.request.user == book.reader

#----------------------User-Registration-----------------------------
@csrf_protect
def register(request):
    if request.method == "POST":
        # take values from registration form
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        # checking if the passwords matches
        if password == password2:
            # checking if the username is not taken
            if User.objects.filter(username=username).exists():
                messages.error(request, f'The username {username} is taken!')
                return redirect('register')
            else:
                # checking if the email does not exist
                if User.objects.filter(email=email).exists():
                    messages.error(request, f'The user with email {email} already registered!')
                    return redirect('register')
                else:
                    # if everything ok, creates new user
                    User.objects.create_user(username=username, email=email, password=password)
                    messages.info(request, f'User {username} has been registered!')
                    return redirect('login')
        else:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')
    return render(request, 'registration/register.html')


#----------------------------------------------------

@login_required
def profile(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f"Profile has been updated")
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'profile.html', context)


#----------------------------------------------------


