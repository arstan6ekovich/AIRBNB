from rest_framework import serializers
from .models import (
    UserProfile, Property, Country, PropertyImage,
    Booking, Review, Payment, Favorite, FavoriteItem
)
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    user_photo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = UserProfile
        fields = (
            'username', 'email', 'password', 'first_name', 'last_name', 'age',
            'phone_number', 'status', 'user_photo'
        )

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = UserProfile.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        user = None
        if username:
            user = authenticate(username=username, password=password)
        elif email:
            from django.contrib.auth import get_user_model
            UserModel = get_user_model()
            try:
                user_obj = UserModel.objects.get(email=email)
                if user_obj.check_password(password):
                    user = user_obj
            except UserModel.DoesNotExist:
                pass

        if user and user.is_active:
            return user
        raise serializers.ValidationError("Неверные учетные данные")

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            'user': {
                'username': instance.username,
                'email': instance.email,
                'first_name': instance.first_name,
                'last_name': instance.last_name,
                'age': instance.age,
                'phone_number': str(instance.phone_number) if instance.phone_number else None,
                'status': instance.status,
                'user_photo': instance.user_photo.url if instance.user_photo else None,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ('id', 'country_logo', 'country')


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ('id', 'image')


class PropertyListSerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    country = CountrySerializer(read_only=True)

    class Meta:
        model = Property
        fields = ('id', 'name', 'price_per_night', 'country', 'city', 'property_type', 'images')


class PropertyDetailSerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    country = CountrySerializer(read_only=True)
    host = UserSerializer(read_only=True)
    reviews = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = (
            'id', 'name', 'description', 'property_type',
            'city', 'country', 'price_per_night', 'max_guests', 'host',
            'created_at', 'updated_at', 'images', 'reviews'
        )

    def get_reviews(self, obj):
        reviews = obj.reviews.all()
        return ReviewSerializer(reviews, many=True).data


class ReviewSerializer(serializers.ModelSerializer):
    guest = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'guest', 'description', 'rating', 'created_at')


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('property', 'description', 'rating')

    def create(self, validated_data):
        user = self.context['request'].user
        return Review.objects.create(guest=user, **validated_data)


class BookingSerializer(serializers.ModelSerializer):
    guest = UserSerializer(read_only=True)
    property = PropertyListSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = ('id', 'guest', 'property', 'start_date', 'end_date', 'status', 'created_at', 'updated_at')

    def validate(self, data):
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError("Дата начала должна быть раньше даты окончания.")
        return data


class PaymentSerializer(serializers.ModelSerializer):
    booking = BookingSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = ('id', 'booking', 'amount', 'status', 'payment_date', 'payment_method')


class FavoriteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ('id', 'user')


class FavoriteItemSerializer(serializers.ModelSerializer):
    favorite = FavoriteSerializer(read_only=True)
    property = PropertyDetailSerializer(read_only=True)

    class Meta:
        model = FavoriteItem
        fields = ('id', 'favorite', 'property', 'added_at')
