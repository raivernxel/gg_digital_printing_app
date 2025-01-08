from django import forms
from .models import TransactionHistory, TransactionTypeMaintenance


class TranHistForm(forms.ModelForm):
    class Meta:
        model = TransactionHistory
        fields = ['user_id', 'amount', 'transaction_type', 'transaction_date', 'transaction_platform',
                  'transaction_number', 'proof', 'remarks']
        widgets = {
            'transaction_date': forms.DateInput(attrs={'type': 'date'})  # HTML5 date picker
        }
