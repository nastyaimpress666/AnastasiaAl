import datetime
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Book, Author, BookInstance, Genre
from .forms import RenewBookForm, RenewBookModelForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

def index(request):
    keyword = "man"
    num_books_keyword = Book.objects.filter(title__icontains=keyword).count()
    keywordforgenre = "fan"
    num_genre_keywordforgenre = Genre.objects.filter(name__icontains=keywordforgenre).count()
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()
    
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    return render(request, 'locallibrary/catalog/index.html', context={
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        "num_books_keyword": num_books_keyword, 
        "keyword": keyword,
        "num_genre_keywordforgenre": num_genre_keywordforgenre,
        'num_visits': num_visits
    })

class BookListView(generic.ListView):
    model = Book
    paginate_by = 2
    template_name = 'locallibrary/catalog/book_list.html'

class BookDetailView(generic.DetailView):
    model = Book
    template_name  'locallibrary/catalog/book_detail.html'

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 2
    template_name 'locallibrary/catalog/author_list.'

class AuthorDetailView(generic.DetailView):
    model = Author
    template_name = 'locallibrary/catalog/author_detail.html'

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'locallibrary/catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10


    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')
        return render(request, 'locallibrary/catalog/index.html'

class LoanedBooksByAllListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'locallibrary/catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 2


 def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)
    if request.method == 'POST':
        form = RenewBookModelForm(request.POST)
        if form.is_valid():
            book_instance.due_back = form.cleaned_data['due_back']
            book_instance.save()
            return HttpResponseRedirect(reverse('all-borrowed'))
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookModelForm(initial={'due_back': proposed_renewal_date})
    
    context = {
        'form': form,
        'book_instance': book_instance,
    }
    return render(request, 'catalog/book_renew_librarian.html', context)

class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/11/2023'}
    permission_required = 'catalog.add_author'
    template_name = 'locallibrary/catalog/author_form.html'

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = '__all__'
    permission_required = 'catalog.change_author'
    template_name = 'locallibrary/catalog/author_form.html'

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.delete_author'
    template_name = 'locallibrary/catalog/author_confirm_delete.html'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception:
            return HttpResponseRedirect(
                reverse("author-delete", kwargs={"pk": self.object.pk})
            )

class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre']
    permission_required = 'catalog.add_book'
    template_name = 'locallibrary/catalog/book_form.html'

class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = '__all__'
    permission_required = 'catalog.change_book'
    template_name = 'locallibrary/catalog/book_form.html'

class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.delete_book'
    template_name = 'locallibrary/catalog/book_confirm_delete.html'