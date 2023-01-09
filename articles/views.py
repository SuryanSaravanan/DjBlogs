from django.shortcuts import get_object_or_404, render, HttpResponse, redirect
from .models import Article
from .forms import LoginForm, UserRegistration, ArticleRegistrationForm, ArticleUpdateForm
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
# Create your views here.


def article_list(request) :
    
    article_list = Article.objects.all().order_by('-published')
    paginator = Paginator(article_list, 5)
    page = request.GET.get('page')

    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)

    return render(request, template_name="articles.html", context={'article_list' : articles, 'page': page})

def article_details(request, slug):
    article = get_object_or_404(Article, slug = slug)
    return render(request, template_name='details.html', context={'article' : article})

def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            
            user = authenticate(request, username = cd['username'], password = cd['password'])

            if user:
                login(request, user)
                return HttpResponse("You are authenticated")
            else:
                return HttpResponse("Invalid Credentials")
    else:
        form = LoginForm()
    
    return render(request, 'account/login.html', {'form' : form})
    
def register(request):
    if request.method == 'POST':
        user_form = UserRegistration(request.POST)

        if user_form.is_valid():
            new_user = user_form.save(commit=False)

            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()

            return render(request,'account/register_done.html', {'user_form' : user_form })
    else:
        user_form = UserRegistration()
    return render(request, 'account/register.html', {'user_form' : user_form })

@login_required
def article_form(request):

    if request.method == "POST":
        article_form = ArticleRegistrationForm(request.POST)
        if article_form.is_valid():
            article = article_form.save(commit=False)
            article.author = request.user
            article.save()
            return redirect('article_list')
    else:
        article_form = ArticleRegistrationForm()
    return render(request, 'account/add_article.html', context={'article_form' : article_form}) 

@login_required
def update_article(request, slug):
    article = get_object_or_404(Article, slug = slug)

    form = ArticleUpdateForm(request.POST or None, instance=article)

    if form.is_valid():
        form.save()
        return redirect('article_list')
    
    return render(request, 'account/update.html', {'form' : form})

def delete_article(request, slug):
    article = get_object_or_404(Article, slug = slug)

    article.delete()
    return redirect('article_list')
