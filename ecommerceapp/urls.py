from django.urls import path
from .views import *

app_name = "ecommerceapp"
urlpatterns = [
    path('', HomeView.as_view(), name="index"),
    path('login/', LoginView.as_view(), name="login"),
    path('all-products/', ProductsView.as_view(), name="allproducts"),
    path('all-products/product-details', ProductDetailView.as_view(), name="productdetail"),
    path('registration/', RegistrationView.as_view(), name="registration"),
    path('logout/', LogOutView.as_view(), name="logout"),


    path('add-to-cart-<int:pro_id>/', AddToCartView.as_view(), name="addtocart"),
    path('my-cart/', MyCartView.as_view(), name="mycart"),
    path('manage-cart/<int:cp_id>/', ManageCartView.as_view(), name="managecart"),
    path('empty-cart/', EmptyCartView.as_view(), name="emptycart"),

    path('checkout/', CheckOutView.as_view(), name="checkoutcart"),
    path('profile/', CustomerProfileView.as_view(), name="customerprofile"),
    path('customerorderdetail/', CustomerOrderDetailView.as_view(), name="customerorderdetail"),
    path("profile/order-<int:pk>/", CustomerOrderDetailView.as_view(), name="customerorderdetail"),


]