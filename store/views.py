from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from carts.models import CartItem
from carts.views import _cart_id
from .models import Product, ReviewRating, ProductGallery
from .forms import ReviewForm
from category.models import Category
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q, Avg



def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True).order_by('id')
        paginator = Paginator(products, 5)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 5)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    context = {
        "products": paged_products,
        "product_count": product_count,
    }

    return render(request, "store/store.html", context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()

        reviews = ReviewRating.objects.filter(product=single_product, status=True)
        average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        product_gallery = ProductGallery.objects.filter(product=single_product)

    except Exception as e:
        raise e

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'reviews': reviews,
        'average_rating': average_rating,
        'product_gallery': product_gallery,
    }

    return render(request, 'store/product_detail.html', context)


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para dejar una reseña.')
            return redirect(url)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            messages.error(request, 'El producto no existe.')
            return redirect('store')

        form = ReviewForm(request.POST)

        if form.is_valid():
            try:
                existing_review = ReviewRating.objects.get(
                    user=request.user,
                    product=product
                )

                existing_review.subject = form.cleaned_data['subject']
                existing_review.review = form.cleaned_data['review']
                existing_review.rating = form.cleaned_data['rating']
                existing_review.status = True
                existing_review.save()

                messages.success(request, 'Tu reseña fue actualizada correctamente.')
                return redirect(url)

            except ReviewRating.DoesNotExist:
                review = form.save(commit=False)
                review.user = request.user
                review.product = product
                review.status = True
                review.save()

                messages.success(request, 'Tu reseña fue enviada correctamente.')
                return redirect(url)

        messages.error(request, 'Por favor verifica los datos de la reseña.')
        return redirect(url)

    return redirect('store')

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    context = {
        'products':products,
        'product_count': product_count
    }        
    return render(request, 'store/store.html', context)