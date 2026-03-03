import pytest
from django.test import Client
from django.urls import reverse

from contacts.models import ContactInfo
from doctors.models import Doctor
from pages.models import AboutPageContent, HomePageContent
from services.models import Service


@pytest.mark.django_db
class TestHomePageView:
    """
    Тесты для главной страницы.
    """

    def test_home_view_status_code(self, client):
        """Тест доступности главной страницы."""
        url = reverse("pages:home")
        response = client.get(url)

        assert response.status_code == 200

    def test_home_view_template(self, client):
        """Тест используемого шаблона."""
        url = reverse("pages:home")
        response = client.get(url)

        assert "pages/home.html" in [t.name for t in response.templates]

    def test_home_view_context_empty(self, client):
        """Тест контекста при отсутствии данных."""
        url = reverse("pages:home")
        response = client.get(url)

        assert "home_content" in response.context
        assert response.context["home_content"] is None
        assert "services" in response.context
        # Исправление: проверяем что QuerySet пустой, а не сравниваем с []
        assert response.context["services"].count() == 0
        assert "doctors" in response.context
        assert response.context["doctors"].count() == 0
        assert "contact_info" in response.context
        assert response.context["contact_info"] is None

    def test_home_view_with_content(self, client):
        """Тест контекста с данными."""
        # Создаем контент для главной
        home_content = HomePageContent.objects.create(
            hero_title="Тестовый заголовок",
            hero_subtitle="Тестовый подзаголовок",
            about_text="Текст о компании",
        )

        # Создаем услуги
        for i in range(5):
            Service.objects.create(
                name=f"Услуга {i}",
                slug=f"usluga-{i}",
                short_description=f"Описание {i}",
                price=1000.00 + i,
                duration=30,
                is_active=True,
            )

        # Создаем врачей
        for i in range(3):
            Doctor.objects.create(
                name=f"Врач {i}",
                slug=f"doctor-{i}",
                specialty="Терапевт",
                bio=f"Биография {i}",
                experience_years=10 + i,
                is_active=True,
            )

        # Создаем контактную информацию
        contact = ContactInfo.objects.create(
            address="Тестовый адрес",
            phone="+7 (999) 123-45-67",
            email="test@example.com",
        )

        url = reverse("pages:home")
        response = client.get(url)

        assert response.context["home_content"] == home_content
        assert len(response.context["services"]) == 5
        assert len(response.context["doctors"]) == 3
        assert response.context["contact_info"] == contact

    def test_home_view_only_active_services(self, client):
        """Тест что отображаются только активные услуги."""
        # Активная услуга
        Service.objects.create(
            name="Активная услуга",
            slug="aktivnaya",
            short_description="Описание",
            price=1000.00,
            duration=30,
            is_active=True,
        )

        # Неактивная услуга
        Service.objects.create(
            name="Неактивная услуга",
            slug="neaktivnaya",
            short_description="Описание",
            price=2000.00,
            duration=45,
            is_active=False,
        )

        url = reverse("pages:home")
        response = client.get(url)

        assert len(response.context["services"]) == 1
        assert response.context["services"][0].name == "Активная услуга"

    def test_home_view_only_active_doctors(self, client):
        """Тест что отображаются только активные врачи."""
        # Активный врач
        Doctor.objects.create(
            name="Активный врач",
            slug="aktivnyy",
            specialty="Терапевт",
            bio="Биография",
            experience_years=10,
            is_active=True,
        )

        # Неактивный врач
        Doctor.objects.create(
            name="Неактивный врач",
            slug="neaktivnyy",
            specialty="Хирург",
            bio="Биография",
            experience_years=15,
            is_active=False,
        )

        url = reverse("pages:home")
        response = client.get(url)

        assert len(response.context["doctors"]) == 1
        assert response.context["doctors"][0].name == "Активный врач"

    def test_home_view_services_limit(self, client):
        """Тест что отображается не больше 6 услуг."""
        # Создаем 10 услуг
        for i in range(10):
            Service.objects.create(
                name=f"Услуга {i}",
                slug=f"usluga-{i}",
                short_description=f"Описание {i}",
                price=1000.00,
                duration=30,
                is_active=True,
            )

        url = reverse("pages:home")
        response = client.get(url)

        assert len(response.context["services"]) == 6  # Должно быть не больше 6

    def test_home_view_doctors_limit(self, client):
        """Тест что отображается не больше 3 врачей."""
        # Создаем 5 врачей
        for i in range(5):
            Doctor.objects.create(
                name=f"Врач {i}",
                slug=f"doctor-{i}",
                specialty="Терапевт",
                bio=f"Биография {i}",
                experience_years=10,
                is_active=True,
            )

        url = reverse("pages:home")
        response = client.get(url)

        assert len(response.context["doctors"]) == 3  # Должно быть не больше 3


@pytest.mark.django_db
class TestAboutPageView:
    """
    Тесты для страницы "О компании".
    """

    def test_about_view_status_code(self, client):
        """Тест доступности страницы."""
        url = reverse("pages:about")
        response = client.get(url)

        assert response.status_code == 200

    def test_about_view_template(self, client):
        """Тест используемого шаблона."""
        url = reverse("pages:about")
        response = client.get(url)

        assert "pages/about.html" in [t.name for t in response.templates]

    def test_about_view_context_empty(self, client):
        """Тест контекста при отсутствии данных."""
        url = reverse("pages:about")
        response = client.get(url)

        assert "about_content" in response.context
        assert response.context["about_content"] is None
        assert "doctors" in response.context
        # Исправление: проверяем что QuerySet пустой, а не сравниваем с []
        assert response.context["doctors"].count() == 0

    def test_about_view_with_content(self, client):
        """Тест контекста с данными."""
        # Создаем контент для страницы
        about_content = AboutPageContent.objects.create(
            title="О компании",
            history_title="Наша история",
            history_text="Текст истории",
            mission_title="Наша миссия",
            mission_text="Текст миссии",
        )

        # Создаем врачей
        for i in range(3):
            Doctor.objects.create(
                name=f"Врач {i}",
                slug=f"doctor-{i}",
                specialty="Терапевт",
                bio=f"Биография {i}",
                experience_years=10 + i,
                is_active=True,
            )

        url = reverse("pages:about")
        response = client.get(url)

        assert response.context["about_content"] == about_content
        assert len(response.context["doctors"]) == 3

    def test_about_view_only_active_doctors(self, client):
        """Тест что отображаются только активные врачи."""
        # Активный врач
        Doctor.objects.create(
            name="Активный врач",
            slug="aktivnyy",
            specialty="Терапевт",
            bio="Биография",
            experience_years=10,
            is_active=True,
        )

        # Неактивный врач
        Doctor.objects.create(
            name="Неактивный врач",
            slug="neaktivnyy",
            specialty="Хирург",
            bio="Биография",
            experience_years=15,
            is_active=False,
        )

        # Создаем контент для страницы
        AboutPageContent.objects.create(history_text="История", mission_text="Миссия")

        url = reverse("pages:about")
        response = client.get(url)

        assert len(response.context["doctors"]) == 1
        assert response.context["doctors"][0].name == "Активный врач"

    def test_about_view_all_doctors(self, client):
        """Тест что отображаются все врачи (без ограничения)."""
        # Создаем 10 врачей
        for i in range(10):
            Doctor.objects.create(
                name=f"Врач {i}",
                slug=f"doctor-{i}",
                specialty="Терапевт",
                bio=f"Биография {i}",
                experience_years=10,
                is_active=True,
            )

        # Создаем контент для страницы
        AboutPageContent.objects.create(history_text="История", mission_text="Миссия")

        url = reverse("pages:about")
        response = client.get(url)

        assert len(response.context["doctors"]) == 10  # Должны быть все
