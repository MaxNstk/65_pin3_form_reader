from django import forms
from django.forms import BaseFormSet, formset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class FormHelperForm(forms.Form):

    form_tag = False
    add_submit=False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        if self.add_submit:
            self.helper.add_input(Submit('submit', 'Enviar'))


class IndexForm(FormHelperForm):

    form_tag = True
    add_submit = True

    
    base_form_upload = forms.FileField(required=False, label='Formulário base')
    json_config_upload = forms.FileField(required=False, label='Json de configuração')


class GroupingForm(FormHelperForm):
    
    rows_amount = forms.IntegerField(label='Quantidade de colunas')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_class = 'grouping-form'
        self.helper.add_input(Submit('submit', 'Definir marcardor', css_class='btn-primary'))

GroupingFormset = formset_factory(GroupingForm, formset=BaseFormSet, extra=1)


class ConfigurationForm(FormHelperForm):
    
    column_amount = forms.IntegerField(label='Quantidade de colunas')
    x_space_between_cells = forms.IntegerField(label='Espaçamento entre células horizontais')
    y_space_between_cells = forms.IntegerField(label='Espaçamento entre células verticais')

