from django.db import models
from django.conf import settings
from django.shortcuts import reverse
# Create your models here.

CATEGORY_CHOICES = (
        ('S','Shirt'),
        ('SW','Sports Wear'),
        ('OW','Out Wear'),
)

LABEL_CHOICES = (
        ('P','primary'),
        ('S','success'),
        ('D','danger'),
)

PAYMENT_METHOD = (
    ('S','Stripe'),
    ('P',"PayPal"),
)


class Item(models.Model):
    item_name = models.CharField(max_length=200)
    item_price = models.FloatField()
    item_discounted_price = models.FloatField(null=True,blank=True)
    item_description = models.TextField()
    item_category = models.CharField(choices=CATEGORY_CHOICES, default='S', max_length=2)
    item_label = models.CharField(choices=LABEL_CHOICES, default='P', max_length=1)
    item_discount = models.PositiveIntegerField(null=True,blank=True)
    item_image = models.CharField(max_length=500,default='http://leeford.in/wp-content/uploads/2017/09/image-not-found.jpg')
    slug = models.SlugField(default='test-product')
    

    class Meta:
        db_table = 'Item'
    
    def __str__(self):
        return self.item_name
    
    def get_absolute_url(self):
        return reverse('core:product', kwargs={
                    'slug':self.slug
        })
    
    def get_add_to_cart_url(self):
           return reverse('core:add-to-cart', kwargs={
                    'slug':self.slug
        })
    
    def get_remove_from_cart_url(self):
        return reverse('core:remove-from-cart', kwargs={
                    'slug':self.slug
        })

    def get_item_price(self):
        if self.item_discounted_price:
            return self.item_discounted_price
        else:
            return self.item_price


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, blank=True, null=True)
    order_item = models.ForeignKey(Item, on_delete = models.CASCADE)
    item_quantity = models.PositiveIntegerField(default=1)
    is_ordered = models.BooleanField(default=False)

    class Meta:
        db_table = 'Order Item'

    def __str__(self):
        return str(self.item_quantity) + " " + self.order_item.item_name

    def get_total_item_price(self):
        return  self.item_quantity * self.order_item.get_item_price()

    def get_total_savings(self):
        if self.order_item.item_discounted_price:
            return (self.order_item.item_price - self.order_item.item_discounted_price)*self.item_quantity
        else:
            return 0

class BillingInformation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete = models.CASCADE)
    street = models.CharField(max_length=300)
    city = models.CharField(max_length=50)
    pin_code = models.CharField(max_length=6)
    state = models.CharField(max_length=100)
    landmark = models.CharField(max_length=500)
    shipping_same_as_billing = models.BooleanField(default=False)
    save_info = models.BooleanField(default=False)
    payment_info = models.CharField(choices=PAYMENT_METHOD,max_length=1)

    def __str__(self):
        return self.street+ " " + self.city+ " " + self.state


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,blank=True, null=True)
    amount = models.FloatField(default=0)
    time_stamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username



class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    order_items = models.ManyToManyField(OrderItem)
    date_of_order = models.DateTimeField()
    is_ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey(BillingInformation,on_delete=models.PROTECT,blank=True,null=True)
    payment = models.ForeignKey(Payment,on_delete=models.SET_NULL,null=True)

    class Meta:
        db_table = 'Order'
    
    def __str__(self):
        return self.user.username

    def get_cart_total(self):
        price = 0
        for i in self.order_items.all():
            price += i.get_total_item_price()
        return price

