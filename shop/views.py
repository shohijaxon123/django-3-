from django.shortcuts import render, redirect
from . import models
from .models import *
from django.contrib.auth.decorators import login_required
from .forms import *
from django.db.models import Q


# Create your views here.
@login_required(login_url='/users/sign_in')
def product_list(request):
    search = request.GET.get('search')
    category = request.GET.get('category')
    brand = request.GET.get('brand')
    product_id = request.GET.get('product')
    products = Product.objects.all()
    slides = Slide.objects.all()

    if product_id:
        product = Product.objects.get(pk=product_id)
        cart_item = CartItem.objects.filter(product=product, customer=request.user)
        if not cart_item:
            CartItem.objects.create(customer=request.user, product=product, quantity=1)
            return redirect('shop:products')
        for item in cart_item:
            item.quantity += 1
            item.save()
    products = products.filter(category=category) if category else products
    products = products.filter(brand=brand) if brand else products
    products = products.filter(Q(title__icontains=search) | Q(description__icontains=search)) if search else products
    return render(request, 'product_list.html', {'products': products, 'slides': slides})


def cart(request):
    cart_items = CartItem.objects.filter(customer=request.user)
    total_price = sum([item.total_price() for item in cart_items])
    total_quantity = sum([item.quantity for item in cart_items])

    return render(request, 'cart.html',
                  {'cart_items': cart_items, 'total_quantity': total_quantity, 'total_price': total_price})


def delete_cart_item(request, pk):
    CartItem.objects.get(pk=pk).delete()
    return redirect('shop:cart')


def edit_cart_item(request, pk):
    cart_item = CartItem.objects.get(pk=pk)
    action = request.GET.get('action')

    if action == 'decrement' and cart_item.quantity == 1:
        cart_item.delete()
        return redirect('shop:cart')
    if action == 'decrement' and cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
        return redirect('shop:cart')
    cart_item.quantity += 1
    cart_item.save()
    return redirect('shop:cart')


def product_detail(request, pk):
    product = Product.objects.get(pk=pk)
    reviews = Review.objects.filter(product=product)
    form = RateForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        rating = form.save(commit=False)
        rating.user = request.user
        rating.product = product
        rating.save()
        return redirect('shop:product_detail', pk=pk)
    return render(request, 'product_detail.html', {'product': product, 'form': form, 'reviews': reviews})


def create_order(request):
    cart_items = CartItem.objects.filter(customer=request.user)
    total_price = sum([item.total_price() for item in cart_items])
    total_quantity = sum([item.quantity for item in cart_items])

    form = OrderForm(request.POST)

    if not cart_items:
        return render(request, 'error.html')

    if request.method == 'POST' and form.is_valid():
        order = Order.objects.create(
            customer=request.user,
            address=request.POST.get('address'),
            phone=request.POST.get('phone'),
            total_price=total_price
        )
        for cart_item in cart_items:
            OrderProduct.objects.create(
                order=order,
                product=cart_item.product,
                amount=cart_item.quantity,
                total=cart_item.total_price()
            )
        cart_items.delete()
        return redirect('shop:products')

    return render(request, 'order_creation_page.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_quantity': total_quantity,
        'form': form
    })


def orders(request):
    orders_list = Order.objects.filter(customer=request.user)
    return render(request, 'orders.html', {'orders': orders_list})
