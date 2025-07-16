from .models import Property, Country
from modeltranslation.translator import TranslationOptions,register

@register(Property)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'city')


@register(Country)
class ProductTranslationOptions(TranslationOptions):
    fields = ('country',)