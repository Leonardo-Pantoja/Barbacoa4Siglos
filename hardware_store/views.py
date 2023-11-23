from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product, ProductCategory, Cart, Client, CartItem, Pedido
from .forms import ProductForm, CategoryForm, CheckoutForm

from django.http import JsonResponse

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from django.contrib.auth import login, authenticate
from django.views.decorators.csrf import csrf_protect
from collections.abc import Iterable
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone


from django.contrib.auth.decorators import user_passes_test

@user_passes_test(lambda u: u.is_staff, login_url='home')
def staff_orders(request):
    pedidos = Pedido.objects.all().order_by('-id')

    # Configura el paginador con 10 pedidos por página
    paginator = Paginator(pedidos, 10)

    # Obtiene el número de página actual
    page = request.GET.get('page')

    try:
        # Obtiene los pedidos para la página actual
        pedidos = paginator.page(page)
    except PageNotAnInteger:
        # Si la página no es un número entero, entrega la primera página
        pedidos = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango, entrega la última página
        pedidos = paginator.page(paginator.num_pages)

    return render(request, 'staff_orders.html', {'pedidos': pedidos, 'paginator': paginator})   

def accept_order(request, pedido_id):
    pedido = Pedido.objects.get(pk=pedido_id)
    pedido.status = 'En Proceso'
    pedido.save()
    return redirect('staff_orders')

def mark_as_delivered(request, pedido_id):
    pedido = Pedido.objects.get(pk=pedido_id)
    pedido.status = 'Entregada'
    pedido.save()
    return redirect('staff_orders')

def tus_pedidos(request):
    lista_pedidos = Pedido.objects.all()

    # Configurar la paginación
    paginator = Paginator(lista_pedidos, 10)  # Muestra 10 pedidos por página
    page = request.GET.get('page')

    try:
        pedidos = paginator.page(page)
    except PageNotAnInteger:
        # Si la página no es un número entero, muestra la primera página
        pedidos = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera del rango, muestra la última página disponible
        pedidos = paginator.page(paginator.num_pages)

    return render(request, 'tu_template.html', {'pedidos': pedidos})

# Product
PRODUCT_LIST_PATH = '/product_list'

def product_list(request):
    products = Product.objects.all()
    categories = ProductCategory.objects.all()
    if not isinstance(categories, Iterable):

        categories = []
    context = {
        'categories': categories,
        'products': products
    }
    return render(request, 'product_list.html', context)


def create_product(request):
    if 'user_id' not in request.session:
        return redirect(PRODUCT_LIST_PATH)
    if not request.user.is_authenticated:
        return redirect(PRODUCT_LIST_PATH)
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()
            return redirect(PRODUCT_LIST_PATH)
    else:
        form = ProductForm()
    return render(request, 'create_product.html', {'form': form})


def edit_product(request, pk):
    if 'user_id' not in request.session:
        return redirect(PRODUCT_LIST_PATH)
    if not request.user.is_authenticated:
        return redirect(PRODUCT_LIST_PATH)
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(instance=product)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()
            return redirect(PRODUCT_LIST_PATH)
    return render(request, 'edit_product.html', {'form': form, 'product': product})


def delete_product(request, pk):
    if 'user_id' not in request.session:
        return redirect(PRODUCT_LIST_PATH)
    if not request.user.is_authenticated:
        return redirect(PRODUCT_LIST_PATH)
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect(PRODUCT_LIST_PATH)

def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'product_detail.html', {'product': product})


# Category
CATEGORY_LIST_PATH = '/category_list'


def category_list(request):
    category = ProductCategory.objects.all()
    return render(request, 'category_list.html', {'category': category})


def create_category(request):
    if 'user_id' not in request.session:
        return redirect(CATEGORY_LIST_PATH)
    if not request.user.is_authenticated:
        return redirect(CATEGORY_LIST_PATH)
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.save()
            return redirect(CATEGORY_LIST_PATH)
    else:
        form = CategoryForm()
    return render(request, 'create_category.html', {'form': form})


def edit_category(request, pk):
    if 'user_id' not in request.session:
        return redirect(CATEGORY_LIST_PATH)
    if not request.user.is_authenticated:
        return redirect(CATEGORY_LIST_PATH)
    category = get_object_or_404(ProductCategory, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        category = form.save(commit=False)
        category.save()
        return redirect(CATEGORY_LIST_PATH)

    return render(request, 'edit_category.html', {'form': form})


def delete_category(request, pk):
    if 'user_id' not in request.session:
        return redirect(CATEGORY_LIST_PATH)
    if not request.user.is_authenticated:
        return redirect(CATEGORY_LIST_PATH)
    category = get_object_or_404(ProductCategory, pk=pk)
    category.delete()
    return redirect(CATEGORY_LIST_PATH)


def category_products(request, pk):
    category = ProductCategory.objects.get(pk=pk)
    products = Product.objects.filter(category_id=category)
    categories = ProductCategory.objects.all()
    
    paginator = Paginator(products, 10)  # Muestra 10 productos por página
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        'categories': categories,
        'category': category,
        'products': products
    }
    
    if products.has_previous():
        context['prev_page'] = products.previous_page_number()
    if products.has_next():
        context['next_page'] = products.next_page_number()
    
    context['total_pages'] = paginator.num_pages
    return render(request, 'product_list.html', context)

# Home


def home(request):
    return render(request, 'home.html')

# Register

@csrf_protect
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

# Login

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                request.session['user_id'] =  user.id
                return redirect(CATEGORY_LIST_PATH)
            else:
                return render(request, 'login.html', {'form': form, 'error_message': 'Invalid user'})
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    logout(request)
    return redirect('home')


def product_list(request):
    products = Product.objects.all()
    categories = ProductCategory.objects.all()
    if not isinstance(categories, Iterable):
        categories = []
    paginator = Paginator(products, 10) # Muestra 10 productos por pagina
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        # Si la pagina excede la cantidad de paginas que hay muestra la ultima disponible
        products = paginator.page(paginator.num_pages)

    context = {
        'categories': categories,
        'products': products
    }
    
    if products.has_previous():
        context['prev_page'] = products.previous_page_number()
    if products.has_next():
        context['next_page'] = products.next_page_number()
    
    context['total_pages'] = paginator.num_pages
    
    return render(request, 'product_list.html', context)

# Cart

@login_required
def cart(request):
    user_cart = Cart.objects.get_or_create(user=request.user)[0]
    cart_items = user_cart.cartitem_set.all()
    total_price = sum(item.subtotal() for item in cart_items)

    return render(request, 'cart.html', {'cart': user_cart, 'total_price': total_price})

@login_required
def view_cart(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    total_price = sum(item.subtotal() for item in cart_items)

    return render(request, 'cart/view_cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    if product.stock >= 1:
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.quantity += 1
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(cart=cart, product=product, quantity=1)
        
        product.stock -= 1
        product.save()

        return redirect('cart')
    else:
        messages.error(request, 'No hay suficiente stock disponible para este producto.')
        return redirect('product_list') 

def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    user_cart = Cart.objects.get(user=request.user)

    try:
        cart_item = CartItem.objects.get(cart=user_cart, product=product)
        quantity_before_removal = cart_item.quantity
        cart_item.delete()

        product.stock += quantity_before_removal
        product.save()

        messages.success(request, 'Producto eliminado del carrito.')
    except CartItem.DoesNotExist:
        messages.error(request, 'El producto no está en tu carrito.')

    return redirect('cart')

def checkout(request):
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['first_name']
            apellido = form.cleaned_data['last_name']
            direccion = form.cleaned_data['address']
            numero_casa = form.cleaned_data['housenumber']
            telefono = form.cleaned_data['phone']
            hora_recogida = form.cleaned_data['pickup_time']
            total_carrito = calcular_total_carrito(request.user)

           # print(f"Nombre: {nombre}, Apellido: {apellido}, Dirección: {direccion}, Número de Casa: {numero_casa}, Teléfono: {telefono}, Hora de Recogida: {hora_recogida}, Total Carrito: {total_carrito}")

            total_carrito = calcular_total_carrito(request.user)

            pedido = Pedido.objects.create(
                user=request.user,
                address=direccion,
                housenumber=numero_casa,
                phone=telefono,
                pickup_time=hora_recogida,
                total_carrito=total_carrito,
            )

            carrito = CartItem.objects.filter(cart__user=request.user)
            for item in carrito:
                item.pedido = pedido
                item.save()

            CartItem.objects.filter(cart__user=request.user).delete()

            return redirect('order_detail', order_id=pedido.id)
    else:
        form = CheckoutForm()

    total_carrito = calcular_total_carrito(request.user)
    return render(request, 'checkout.html', {'form': form, 'total_carrito': total_carrito})



def calcular_total_carrito(user):
    carrito = CartItem.objects.filter(cart__user=user)
    total = sum(item.product.price * item.quantity for item in carrito)
    return total

# Orders

def orders(request):
    try:
        pedidos = Pedido.objects.filter(user=request.user)
        print("Pedidos:", pedidos)  # Agrega esta línea para depuración
    except Pedido.DoesNotExist:
        pedidos = []

    return render(request, 'orders.html', {'pedidos': pedidos})

def order_detail(request, order_id):
    order = get_object_or_404(Pedido, id=order_id)
    return render(request, 'order_detail.html', {'order': order})

def faq(request):
    return render(request, 'faq.html')

def horarios(request):
    return render(request, 'horarios.html')
