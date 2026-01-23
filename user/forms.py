from django import forms
from django.contrib.auth.models import User
from user.models import UserRole


class CreateUserForm(forms.ModelForm):
    password = forms.CharField(
        required=False,   # 👈 kritik
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    role = forms.ChoiceField(
        choices=UserRole.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'required': True})
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'required': True,
                'pattern': r'.+@putzmeister\.com$',   # 👈 kritik
                'title': 'Email must be a valid @putzmeister.com address'
            }),
        }

class LoginForm(forms.Form):
    username = forms.CharField(
        label="Username", 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autofocus': True
        }))
    
    password = forms.CharField(
        label="Password", 
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        }))



class RegisterForm(forms.Form):
    username = forms.CharField(max_length=50, label="Username", widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autofocus': True
        }))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Company E-mail'
        }))
    password = forms.CharField(max_length=20, label="Password", widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        }))
    confirm = forms.CharField(max_length=20, label="Confirm Password",widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        }))

    # confirm process
    def clean(self):
        username = self.cleaned_data.get("username") 
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password") 
        confirm = self.cleaned_data.get("confirm")

        if password and confirm and password != confirm:
            raise forms.ValidationError("Passwords doesn't match")
        

        values = {
            "username": username,
            "password": password,
            "email":email 
        }

        return values
    