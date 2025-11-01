from collections.abc import Sequence
from typing import Any

from django.contrib.auth import get_user_model
from factory import Faker, post_generation
from factory import Sequence as FactorySequence
from factory.django import DjangoModelFactory

User = get_user_model()


class UserFactory(DjangoModelFactory):
    email = FactorySequence(lambda n: f"user{n}@example.com")
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    is_active = True
    is_staff = False
    is_superuser = False

    @post_generation
    def password(self, create: bool, extracted: Sequence[Any], **kwargs):
        password = (
            extracted
            if extracted
            else Faker(
                "password",
                length=42,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ).evaluate(None, None, extra={"locale": None})
        )
        self.set_password(password)

    class Meta:
        model = User
        django_get_or_create = ["email"]
