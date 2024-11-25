from django import forms
from application.models import Leave, Employee


class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['start_date', 'end_date', 'description', 'substitute', 'employee']



    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        self.fields['substitute'].empty_label = "Substitute employee"
        self.fields['substitute'].queryset = Employee.objects.filter(
            role='staff').exclude(id=request.user.id)

        self.fields['start_date'].widget.attrs.update({'class': 'datepicker'})
        self.fields['end_date'].widget.attrs.update({'class': 'datepicker'})
        self.fields['employee'].widget = forms.HiddenInput()
        self.fields['employee'].initial = request.user.id

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError(
                "Başlangıç tarihi, bitiş tarihinden büyük olamaz.")

        return cleaned_data
