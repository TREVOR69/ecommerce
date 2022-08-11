from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
from django.views.generic import TemplateView, View, CreateView, FormView, DetailView
from django.urls import reverse_lazy
from .forms import CheckOutForm, CustomerRegistrationForm, CustomerLoginForm
from django.contrib.auth import authenticate, login, logout
from django_daraja.mpesa.core import MpesaClient


# Create your views here.

class EcomMixin(object):
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            if request.user.is_authenticated and request.user.customer:
                cart_obj.customer = request.user.customer
                cart_obj.save()
        return super().dispatch(request, *args, **kwargs)


class HomeView(EcomMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['Product_list'] = Product.objects.all()
        return context


class ProductsView(EcomMixin, TemplateView):
    template_name = 'products.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allcategories'] = Category.objects.all()
        return context


class ProductDetailView(EcomMixin, TemplateView):
    template_name = 'productdetail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # url_slug = kwargs['slug']
        # product = Product.object.get(slug=url_slug)
        context['product'] = Product.objects.get()
        return context


class AddToCartView(EcomMixin, TemplateView):
    template_name = 'addtocart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get product id from requested url
        product_id = self.kwargs['pro_id']

        # get product
        product_obj = Product.objects.get(id=product_id)

        # check if cart exists
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            product_in_cart = cart_obj.cartproduct_set.filter(product=product_obj)
            # item already exists in cart
            if product_in_cart.exists():
                cartproduct = product_in_cart.last()
                cartproduct.quantity += 1
                cartproduct.subtotal += product_obj.price
                cartproduct.save()
                cart_obj.total += product_obj.price
                cart_obj.save()
            # new item is added in cart
            else:
                cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj, rate=product_obj.price,
                                                         quantity=1, subtotal=product_obj.price)
                cart_obj.total += product_obj.price
                cart_obj.save()

        else:
            cart_obj = Cart.objects.create(total=0)
            self.request.session['cart_id'] = cart_obj.id
            cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj, rate=product_obj.price,
                                                     quantity=1, subtotal=product_obj.price)
            cart_obj.total += product_obj.price
            cart_obj.save()

            return context


class ManageCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        cp_id = self.kwargs["cp_id"]
        action = request.GET.get("action")
        cp_obj = CartProduct.objects.get(id=cp_id)
        cart_obj = cp_obj.cart

        if action == "inc":
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cart_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save()

        elif action == "dcr":
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()

        elif action == "rmv":
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()

        else:
            pass
        return redirect("ecommerceapp:mycart")


class EmptyCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            cart.cartproduct_set.all().delete()
            cart.total = 0
            cart.save()
        return redirect("ecommerceapp:mycart")


class MyCartView(EcomMixin, TemplateView):
    template_name = 'mycart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get('cart_id', None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = None
        context['cart'] = cart

        return context


class CheckOutView(EcomMixin, CreateView):
    template_name = 'checkout.html'
    form_class = CheckOutForm
    success_url = reverse_lazy("ecommerceapp:index")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.customer:
            pass
        else:
            return redirect("/login/?next=/checkout/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_obj = None
        context['cart'] = cart_obj
        return context

    def form_valid(self, form):
        cart_id = self.request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total
            form.instance.discount = 0
            form.instance.total = cart_obj.total
            form.instance.order_status = "pending"
            del self.request.session['cart_id']
        else:
            return redirect("ecommerceapp:index")
        return super().form_valid(form)


class RegistrationView(CreateView):
    template_name = 'register.html'
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy("ecommerceapp:index")

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        email = form.cleaned_data.get("username")
        user = User.objects.create_user(username, email, password)
        form.instance.user = user
        login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url


class LogOutView(View):
    def get(self, request):
        logout(request)
        return redirect("ecommerceapp:index")


class LoginView(FormView):
    template_name = 'login.html'
    form_class = CustomerLoginForm
    success_url = reverse_lazy("ecommerceapp:index")

    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pwd = form.cleaned_data["password"]
        usr = authenticate(username=uname, password=pwd)
        if usr is not None and Customer.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name,
                          {"form": self.form_class, "error": "Wrong Username or Password!"})

        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url


class CustomerProfileView(FormView):
    template_name = 'profile.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.customer:
            pass
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        context['customer'] = customer
        orders = Order.objects.filter(cart__customer=customer)
        context["orders"] = orders
        return context


class CustomerOrderDetailView(DetailView):
    template_name = "customerorderdetail.html"
    model = Order
    context_object_name = "ord_obj"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            order_id = self.kwargs["pk"]
            order = Order.objects.get(id=order_id)
            if request.user.customer != order.cart.customer:
                return redirect("ecommerceapp:customerprofile")
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)
