import pytest
from django.db import IntegrityError
from django.urls import reverse

from services.models import Service


@pytest.mark.django_db
class TestServiceModel:
    """
    Тесты для модели Service.
    """

    def test_service_str_method(self):
        """Тест строкового представления услуги."""
        service = Service.objects.create(
            name="УЗИ брюшной полости",
            slug="uzi-bryushnoy-polosti",
            short_description="Описание",
            price=2500.00,
            duration=20,
        )
        assert str(service) == "УЗИ брюшной полости"

    def test_slug_unique(self):
        """Тест уникальности slug."""
        Service.objects.create(
            name="Услуга 1",
            slug="test-slug",
            short_description="Описание 1",
            price=1000.00,
            duration=30,
        )

        # Пытаемся создать вторую услугу с тем же slug
        with pytest.raises(IntegrityError):
            Service.objects.create(
                name="Услуга 2",
                slug="test-slug",
                short_description="Описание 2",
                price=2000.00,
                duration=45,
            )

    def test_get_absolute_url(self):
        """Тест метода get_absolute_url."""
        service = Service.objects.create(
            name="Тестовая услуга",
            slug="test-service",
            short_description="Описание",
            price=1000.00,
            duration=30,
        )
        url = service.get_absolute_url()
        assert url == reverse("services:service_detail", args=["test-service"])

    def test_get_price_formatted(self):
        """Тест форматирования цены."""
        service = Service.objects.create(
            name="Тестовая услуга",
            slug="test-service",
            short_description="Описание",
            price=1500.50,
            duration=30,
        )
        assert service.get_price_formatted() == "1500.50 ₽"

        service.price = 1000.00
        service.save()
        assert service.get_price_formatted() == "1000.00 ₽"

    def test_ordering(self):
        """Тест сортировки услуг."""
        # Создаем услуги с уникальными slug
        service1 = Service.objects.create(
            name="Б услуга",
            slug="b-usluga",
            short_description="Описание 1",
            price=1000.00,
            duration=30,
            order=2,
        )
        service2 = Service.objects.create(
            name="А услуга",
            slug="a-usluga",
            short_description="Описание 2",
            price=2000.00,
            duration=45,
            order=1,
        )
        service3 = Service.objects.create(
            name="В услуга",
            slug="v-usluga",
            short_description="Описание 3",
            price=3000.00,
            duration=60,
            order=1,
        )

        services = Service.objects.all()
        assert services[0] == service2
        assert services[1] == service3
        assert services[2] == service1

    def test_is_active_filtering(self):
        """Тест фильтрации по активности."""
        Service.objects.create(
            name="Активная услуга",
            slug="aktivnaya",
            short_description="Описание",
            price=1000.00,
            duration=30,
            is_active=True,
        )
        Service.objects.create(
            name="Неактивная услуга",
            slug="neaktivnaya",
            short_description="Описание",
            price=2000.00,
            duration=45,
            is_active=False,
        )

        active_services = Service.objects.filter(is_active=True)
        assert active_services.count() == 1
        assert active_services[0].name == "Активная услуга"

    def test_meta_verbose_names(self):
        """Тест verbose names в Meta классе."""
        assert Service._meta.verbose_name == "Услуга"
        assert Service._meta.verbose_name_plural == "Услуги"
        assert Service._meta.ordering == ["order", "name"]

    def test_field_verbose_names(self):
        """Тест verbose names полей."""
        assert Service._meta.get_field("name").verbose_name == "Название услуги"
        assert Service._meta.get_field("slug").verbose_name == "URL-идентификатор"
        assert (
            Service._meta.get_field("short_description").verbose_name
            == "Краткое описание"
        )
        assert (
            Service._meta.get_field("full_description").verbose_name
            == "Полное описание"
        )
        assert Service._meta.get_field("price").verbose_name == "Цена"
        assert (
            Service._meta.get_field("duration").verbose_name == "Длительность (минут)"
        )
        assert Service._meta.get_field("is_active").verbose_name == "Активна"
        assert Service._meta.get_field("order").verbose_name == "Порядок сортировки"

    def test_help_texts(self):
        """Тест help_text полей."""
        assert "Уникальный идентификатор" in Service._meta.get_field("slug").help_text
        assert (
            "Отображается в списке"
            in Service._meta.get_field("short_description").help_text
        )
        assert (
            "Детальное описание"
            in Service._meta.get_field("full_description").help_text
        )
        assert "Стоимость услуги" in Service._meta.get_field("price").help_text
        assert "Среднее время" in Service._meta.get_field("duration").help_text
        assert "Отображать ли услугу" in Service._meta.get_field("is_active").help_text
        assert "Чем меньше число" in Service._meta.get_field("order").help_text

    def test_timestamps(self):
        """Тест автоматических временных меток."""
        import datetime

        service = Service.objects.create(
            name="Тестовая услуга",
            slug="test-service",
            short_description="Описание",
            price=1000.00,
            duration=30,
        )

        assert service.created_at is not None
        assert service.updated_at is not None
        assert isinstance(service.created_at, datetime.datetime)
        assert isinstance(service.updated_at, datetime.datetime)

        old_updated = service.updated_at
        service.name = "Новое название"
        service.save()
        service.refresh_from_db()
        assert service.updated_at > old_updated
