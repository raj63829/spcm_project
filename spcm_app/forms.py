"""
Django Forms for SPCM - Enhanced with Authentication
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Portfolio, PortfolioPosition, Stock, UserProfile
#Developed By RAJ SHARMA
class StockSearchForm(forms.Form):
    """Form for searching stocks"""
    symbol = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter stock symbol (e.g., AAPL, TATA)',
            'autocomplete': 'off'
        })
    )
#Developed By RAJ SHARMA
class PortfolioForm(forms.ModelForm):
    """Form for creating/editing portfolios"""
    class Meta:
        model = Portfolio
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Portfolio Name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Portfolio Description (optional)'
            })
        }

class PositionForm(forms.ModelForm):
    """Form for adding positions to portfolio"""
    stock_symbol = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Stock Symbol'
        })
    )
    
    class Meta:
        model = PortfolioPosition
        fields = ['shares', 'average_price', 'purchase_date']
        widgets = {
            'shares': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.0001',
                'min': '0'
            }),
            'average_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'purchase_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }
    
    def clean_stock_symbol(self):
        symbol = self.cleaned_data['stock_symbol'].upper()
        try:
            stock = Stock.objects.get(symbol=symbol)
            return stock
        except Stock.DoesNotExist:
            raise forms.ValidationError(f'Stock {symbol} not found.')
    
    def save(self, commit=True):
        position = super().save(commit=False)
        position.stock = self.cleaned_data['stock_symbol']
        if commit:
            position.save()
        return position

class CustomUserCreationForm(UserCreationForm):
    """Enhanced user creation form"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Create user profile
            UserProfile.objects.create(user=user)
        return user

class CustomAuthenticationForm(AuthenticationForm):
    """Enhanced login form"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )

class UserProfileForm(forms.ModelForm):
    """Form for editing user profile"""
    class Meta:
        model = UserProfile
        fields = ['risk_tolerance', 'investment_experience', 'preferred_sectors']
        widgets = {
            'risk_tolerance': forms.Select(attrs={'class': 'form-control'}),
            'investment_experience': forms.Select(attrs={'class': 'form-control'}),
            'preferred_sectors': forms.CheckboxSelectMultiple(),
        }

class UserUpdateForm(forms.ModelForm):
    """Form for updating user information"""
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class StockAnalysisForm(forms.Form):
    """Form for stock analysis parameters"""
    TIMEFRAME_CHOICES = [
        ('1D', '1 Day'),
        ('1W', '1 Week'),
        ('1M', '1 Month'),
        ('3M', '3 Months'),
        ('6M', '6 Months'),
        ('1Y', '1 Year'),
    ]
    
    timeframe = forms.ChoiceField(
        choices=TIMEFRAME_CHOICES,
        initial='1M',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    include_sentiment = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    include_technical = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
