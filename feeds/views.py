from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .models import Product, Zone, UserProfile, Order, OrderItem

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Get additional fields
            phone = request.POST.get('phone_number')
            zone_id = request.POST.get('zone')
            zone = Zone.objects.get(id=zone_id)
            
            # Create user profile
            UserProfile.objects.create(
                user=user,
                phone_number=phone,
                zone=zone
            )
            
            login(request, user)
            messages.success(request, f'Welcome to Santamore Feeds, {user.username}!')
            return redirect('products')
    else:
        form = UserCreationForm()
    
    zones = Zone.objects.all()
    return render(request, 'register.html', {'form': form, 'zones': zones})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('products')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')

@login_required
def products(request):
    products = Product.objects.filter(stock__gt=0)
    user_zone = request.user.userprofile.zone
    
    # Add discounted prices to products
    for product in products:
        product.display_price = product.get_price_for_zone(user_zone)
    
    context = {
        'products': products,
        'zone': user_zone,
        'discount_active': user_zone.discount_active() if user_zone else False,
    }
    return render(request, 'products.html', context)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Get or create cart (stored in session)
    cart = request.session.get('cart', {})
    
    # Add product to cart
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'price': float(product.get_price_for_zone(request.user.userprofile.zone)),
            'quantity': 1,
            'weight': product.weight
        }
    
    request.session['cart'] = cart
    messages.success(request, f'{product.name} added to cart!')
    return redirect('products')

@login_required
def view_cart(request):
    cart = request.session.get('cart', {})
    
    total = sum([item['price'] * item['quantity'] for item in cart.values()])
    total_weight = sum([item['weight'] * item['quantity'] for item in cart.values()])
    
    context = {
        'cart': cart,
        'total': total,
        'total_weight': total_weight,
    }
    return render(request, 'cart.html', context)

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.warning(request, 'Your cart is empty!')
        return redirect('products')
    
    # Calculate total
    total = sum([item['price'] * item['quantity'] for item in cart.values()])
    
    # Create order
    order = Order.objects.create(
        user=request.user,
        zone=request.user.userprofile.zone,
        total_amount=total
    )
    
    # Create order items
    for product_id, item in cart.items():
        product = Product.objects.get(id=int(product_id))
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item['quantity'],
            price=item['price']
        )
    
    # Clear cart
    request.session['cart'] = {}
    
    # Redirect to payment
    return redirect('initiate_payment', order_id=order.id)