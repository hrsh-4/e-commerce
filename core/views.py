from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
import stripe 

from django.contrib import messages
# token = stripe.api_key
stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"
# `source` is obtained with Stripe.js; see https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token
# stripe.api_key = settings.STRIPE_SECRET_KEY
# Create your views here.

from .models import Item, OrderItem, Order, BillingInformation, Payment
from .forms import CheckoutForm
# def home(request):
#     context = {
#         'items': Item.objects.all()
#     }

#     return render(request,'home.html',context)

class HomeView(ListView):
    model = Item
    
    template_name = 'home.html'

class ItemDetails(DetailView):
    model = Item
    template_name = 'product.html'

@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        order_item=item,
        user=request.user,
        is_ordered=False
        )
    order_qs = Order.objects.filter(user=request.user, is_ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        print(order)
        if order.order_items.filter(order_item__slug=item.slug).exists():
            order_item.item_quantity += 1
            order_item.save()
        else:
                order.order_items.add(order_item)

    else:
            date_of_order = timezone.now()
            order = Order.objects.create(user=request.user,date_of_order= date_of_order)
            order.order_items.add(order_item)
    return redirect("core:order-summary")

@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item,slug=slug)
    order_qs = Order.objects.filter(user=request.user, is_ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.order_items.filter(order_item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                                order_item=item,
                                user=request.user,
                                is_ordered=False
                                )[0]
            order.order_items.filter(order_item__slug=item.slug).delete()
        else:
            return redirect("core:product",slug=slug)
    else:
        return redirect("core:product",slug=slug)

    return redirect("core:product",slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item,slug=slug)
    order_qs = Order.objects.filter(user=request.user, is_ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.order_items.filter(order_item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                                order_item=item,
                                user=request.user,
                                is_ordered=False
                                )[0]
            if order_item.item_quantity > 1:
                order_item.item_quantity -= 1
                order_item.save()
            else:
                order.order_items.filter(order_item__slug=item.slug).delete()
        
        else:
            return redirect("core:order-summary")
    else:
        return redirect("core:order-summary")

    return redirect("core:order-summary")



class OrderSummary(LoginRequiredMixin,View):
    def get(self, *args, **kwargs):
        if Order.order_items:
            order = Order.objects.get(user=self.request.user, is_ordered=False)
            
            context = {'object':order}
            return render(self.request,'order-summary.html',context)
        else:
            return render(self.request,'empty-cart.html')



class CheckoutView(LoginRequiredMixin,View):
   

    def get(self,*args,**kwargs):

        form = CheckoutForm
        context = {'form':form}
        return render(self.request,'checkout.html',context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        order = Order.objects.get(user=self.request.user, is_ordered=False)
        if form.is_valid():
            street = form.cleaned_data.get('street')
            city = form.cleaned_data.get('city')
            state = form.cleaned_data.get('state')
            landmark = form.cleaned_data.get('landmark')
            shipping_same_as_billing = form.cleaned_data.get('shipping_same_as_billing')
            save_info = form.cleaned_data.get('save_info')
            payment_info = form.cleaned_data.get('payment_info')

            billing_address = BillingInformation(
                user = self.request.user,
                street = street,
                city = city,
                state = state,
                landmark = landmark,
                shipping_same_as_billing = shipping_same_as_billing,
                save_info = save_info,
                payment_info = payment_info
            )

            billing_address.save()
            order.billing_address = billing_address
            order.save()


        return redirect('core:order-summary')

class PaymentView(LoginRequiredMixin, View):

    def get(self,*args,**kwargs):
        order = Order.objects.get(user=self.request.user, is_ordered=False)
        context = {
            'order':order
        }
        return render(self.request,'payment.html',context)
    
    def post(self,*args,**kwargs):
        order = Order.objects.get(user=self.request.user,is_ordered=False)
            # token = self.request.POST.get('stripeToken')
        order_amount =  int(order.get_cart_total())
        try:
            charge = stripe.Charge.create(
                    amount=order_amount,
                    currency="usd",
                    source = self.request.POST.get('stripeToken')
                    )

            payment = Payment()
            payment.stripe_charge_id = charge['id']
            print(charge['id'])
            payment.amount = order_amount
            payment.user = self.request.user
            payment.save()

            order.is_ordered = True
            order.payment = payment
            
            order.save()
            messages.success(self.request,"YaYY!! Your order has been successfully placed")
            return redirect('/')
        except stripe.error.CardError as e:
            # Problem with the card
            messages.error(self.request,"Card error")
            return redirect("/")
            # pass
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            
            messages.error(self.request,"Rate limit error")
            # pass
            return redirect("/")
        except stripe.error.InvalidRequestError as e:
            print(e)
            # Invalid parameters were supplied to Stripe API
            # pass
            
            messages.error(self.request,"Invalid request  error")
            return redirect("/")
        except stripe.error.AuthenticationError as e:
            # Authentication Error: Authentication with Stripe API failed (maybe you changed API keys recently)
            # pass
            
            messages.error(self.request,"Authentication error")
            return redirect("/")
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            # pass
            
            messages.error(self.request,"API connection error")
            return redirect("/")
        except stripe.error.StripeError as e:
            # Stripe Error
            # pass
            
            messages.error(self.request,"Stripe error")
            return redirect("/")
       


        