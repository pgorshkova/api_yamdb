import datetime as dt

from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import serializers

from reviews.models import Category, Comments, Genre, Review, Title
from users.models import User
from users.validators import username_me


class SignUpSerializer(serializers.Serializer):
    """Serializer для входа"""
    username = serializers.RegexField(max_length=settings.LIMIT_USERNAME,
                                      regex=r'^[\w.@+-]+\Z', required=True)
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise ValidationError(
                'Пользователь с таким email уже существует.'
            )

        return value

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Запрещено использовать "me" в качестве имени пользователя'
            )
        elif User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'Данный username (имя) занято, '
                'используйте другое '
            )

        return value


class TokenRegSerializer(serializers.Serializer):
    """Serializer для токенов"""
    username = serializers.RegexField(max_length=settings.LIMIT_USERNAME,
                                      regex=r'^[\w.@+-]+\Z', required=True)
    confirmation_code = serializers.CharField(max_length=settings.LIMIT_CHAT,
                                              required=True)

    def validate_username(self, value):
        """Валидация имени"""
        return username_me(value)


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователей"""
    username = serializers.RegexField(max_length=settings.LIMIT_USERNAME,
                                      regex=r'^[\w.@+-]+\Z', required=True)

    class Meta:
        abstract = True
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')

    def validate_username(self, value):
        """Валидация имени"""
        if (
            self.context.get('request').method == 'POST'
            and User.objects.filter(username=value).exists()
        ):
            raise ValidationError(
                'Пользователь с таким именем уже существует.'
            )
        return username_me(value)


class UserEditSerializer(UserSerializer):
    """Serializer для пользователей"""
    role = serializers.CharField(read_only=True)


class CategorySerializer(serializers.ModelSerializer):
    """Serializer для категорий"""
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Serializer для жанров."""
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Serializer для произведений."""
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField(default=1)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category',
                  )
        read_only_fields = ('id', 'name', 'year', 'rating',
                            'description', 'genre', 'category',
                            )


class TitlePostSerialzier(serializers.ModelSerializer):
    """Serializer для произведений (POST запросы)."""
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    rating = serializers.IntegerField(required=False)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')

    def validate_year(self, value):
        current_year = dt.date.today().year
        if (value > current_year):
            raise serializers.ValidationError(
                'Год произведения не может быть больше текущего.'
            )
        return value

    def to_representation(self, instance):
        """Изменяет отображение информации в ответе (response)
         после POST запроса, в соответствии с ТЗ"""
        return TitleSerializer(instance).data


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer для отзывов и оценок."""
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    def validate_score(self, score):
        if not 1 <= score <= 10:
            raise serializers.ValidationError(
                'Оценка рейтинга - это целое число в диапазоне от 1 до 10.'
            )
        return score

    def validate(self, data):
        """Валидация для отзывов и оценок"""
        if self.context['request'].method != 'POST':
            return data

        author = self.context['request'].user
        title_id = (self.context['request'].
                    parser_context['kwargs']['title_id']
                    )

        if Review.objects.filter(
                author=author, title=title_id).exists():
            raise serializers.ValidationError(
                'Может существовать только один отзыв!'
            )
        return data

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    """Serializer для комментариев"""
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comments
        fields = ('id', 'text', 'pub_date', 'author', 'review')
        read_only_fields = ('review',)
