from django.urls import path, include
from core import views
app_name = 'core'

urlpatterns = [
    path('',views.HomeView.as_view(), name = 'home'),
    path('product/<slug>/', views.ItemDetails.as_view(),name='product'),
    path('add_to_cart/<slug>/', views.add_to_cart, name='add-to-cart'),
    path('remove_from_cart/<slug>/', views.remove_from_cart, name='remove-from-cart'),
    path('order-summary/',views.OrderSummary.as_view(),name='order-summary'),
    path('remove_single_item/<slug>/',views.remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path('checkout/',views.CheckoutView.as_view(),name='checkout'),
    path('payment/<payment_info>/',views.PaymentView.as_view(), name='payment'),

]