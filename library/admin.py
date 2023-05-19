from django.contrib import admin
from .models import *


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'display_books')

class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    # prevents from deleting instance
    readonly_fields = ('instance_id',)
    can_delete = False
    extra = 0 # turns off additional empty lines for input

class BookAmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'description', 'display_genre')
    list_filter = ('author',)
    search_fields = ('title',)
    inlines = [BooksInstanceInline]

class BookInstanceAdmin(admin.ModelAdmin):
    def change_format(self, obj):
        return obj.due_back.strftime('%Y-%m-%d')

    list_display = ('book', 'book_status', 'due_back', 'change_format')
    list_editable = ('due_back', 'book_status')
    list_filter = ('book_status',)
    search_fields = ('instance_id', 'book__title')
    fieldsets = (
        ('General', {'fields': ('instance_id', 'book')}),
        ('Availability', {'fields': ('book_status', 'due_back', 'reader')})
    )

class BookReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'date_created', 'reviewer', 'content')



admin.site.register(Author, AuthorAdmin)
admin.site.register(Book, BookAmin)
admin.site.register(Genre)
admin.site.register(BookInstance, BookInstanceAdmin)
admin.site.register(BookReview, BookReviewAdmin)
#admin.site.register(Profile)
