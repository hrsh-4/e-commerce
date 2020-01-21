from django import forms

PAYMENT_METHOD = (
    ('S','Stripe'),
    ('P',"PayPal"),
)

class CheckoutForm(forms.Form):
    street = forms.CharField(max_length=300,required=True, widget=forms.TextInput)
    city = forms.CharField(max_length=50,required=True,widget=forms.TextInput)
    pin_code = forms.CharField(max_length=6, min_length=6,required=True)
    state = forms.CharField(max_length=50,required=True,widget=forms.TextInput)
    landmark = forms.CharField(max_length=300,widget=forms.Textarea)
    shipping_same_as_billing = forms.BooleanField(required=False,widget=forms.CheckboxInput)
    save_info = forms.BooleanField(required=False,widget=forms.CheckboxInput)
    payment_method = forms.ChoiceField(required=True,choices=PAYMENT_METHOD,widget=forms.RadioSelect)