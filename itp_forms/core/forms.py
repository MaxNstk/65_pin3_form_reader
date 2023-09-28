from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button,Layout, Div, Field, HTML

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



# class GroupingForm(FormHelperForm):
    
#     rows_amount = forms.IntegerField(label='Quantidade de colunas')

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.helper.form_class = 'grouping-form'
#         self.helper.add_input(Submit('submit', 'Definir marcardor', css_class='btn-primary'))
        
# GroupingFormset = formset_factory(GroupingForm, formset=BaseFormSet, extra=1)



class ConfigurationForm(FormHelperForm):

    form_tag = True
    
    column_amount = forms.IntegerField(label='Quantidade de colunas')
    y_space_between_cells = forms.FloatField(label='Espaçamento entre células verticais')
    x_space_between_cells = forms.FloatField(label='Espaçamento entre células horizontais')

    column_amount = forms.IntegerField(label='Quantidade de colunas')

    first_group_row_amount = forms.IntegerField(label='Quantidade de linhas do 1º Agrupamento')
    second_group_row_amount = forms.IntegerField(label='Quantidade de linhas do 2º Agrupamento')
    third_group_row_amount = forms.IntegerField(label='Quantidade de linhas do 3º Agrupamento')
    fourth_group_row_amount = forms.IntegerField(label='Quantidade de linhas do 4º Agrupamento')


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Div(
                Div(Button('update_image','Recarregar imagem',css_class='btn btn-primary w-100', css_id='btn-update-image'), css_class='col-lg-6'),
                Div(Button('update_image','Atualizar Informações',css_class='btn btn-primary w-100', css_id='btn-update-info'), css_class='col-lg-6'),
                css_class='row'
            ),
            Div(
                Div(Field('column_amount'),css_class='col-lg-12'),
                Div(Field('y_space_between_cells'),css_class='col-lg-12'),
                Div(Field('x_space_between_cells'),css_class='col-lg-12'),
                css_class='row'
            ),
            Div(
                Div(
                    Div(
                        Div(Field('first_group_row_amount'),css_class='col-lg-12'),
                        Div(Button('Limpar', 'Definir célula inicial', css_class='btn btn-primary w-100', css_id='bt-set-grouping-1'),css_class='col-lg-12'),
                        css_class='row'
                    ),
                css_class="card-body"),
            css_class="card"),
            Div(
                Div(
                    Div(
                        Div(Field('second_group_row_amount'),css_class='col-lg-12'),
                        Div(Button('Limpar', 'Definir célula inicial', css_class='btn btn-primary w-100', css_id='bt-set-grouping-2'),css_class='col-lg-12'),
                        css_class='row'
                    ),
                css_class="card-body"),
            css_class="card"),
            Div(
                Div(
                    Div(
                        Div(Field('third_group_row_amount'),css_class='col-lg-12'),
                        Div(Button('Limpar', 'Definir célula inicial', css_class='btn btn-primary w-100', css_id='bt-set-grouping-3'),css_class='col-lg-12'),
                        css_class='row'
                    ),
                css_class="card-body"),
            css_class="card"),
            Div(
                Div(
                    Div(
                        Div(Field('fourth_group_row_amount'),css_class='col-lg-12'),
                        Div(Button('Limpar', 'Definir célula inicial', css_class='btn btn-primary w-100', css_id='bt-set-grouping-2'),css_class='col-lg-12'),
                        css_class='row'
                    ),
                css_class="card-body"),
            css_class="card"),
        )
        

