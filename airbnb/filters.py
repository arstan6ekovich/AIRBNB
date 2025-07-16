from django_filters import rest_framework as filters
from .models import Property


class PropertyFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price_per_night", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price_per_night", lookup_expr='lte')
    city = filters.CharFilter(field_name='city', lookup_expr='icontains')
    property_type = filters.CharFilter(field_name='property_type', lookup_expr='iexact')

    class Meta:
        model = Property
        fields = ['city', 'property_type', 'min_price', 'max_price']
