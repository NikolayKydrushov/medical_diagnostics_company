import pytest
from django.test import Client
from django.urls import reverse

from doctors.models import Doctor
from services.models import Service


@pytest.mark.django_db
class TestDoctorListView:
    """
    Тесты для списка врачей.
    """

    def test_doctor_list_view_get(self, client):
        """Тест GET запроса к списку врачей."""
        url = reverse("doctors:doctor_list")
        response = client.get(url)

        assert response.status_code == 200
        assert "doctors/doctor_list.html" in [t.name for t in response.templates]
        assert "doctors" in response.context
        assert "specialties" in response.context
        assert "search_query" in response.context
        assert "current_specialty" in response.context

    def test_doctor_list_only_active(self, client):
        """Тест что отображаются только активные врачи."""
        Doctor.objects.create(
            name="Активный врач",
            slug="aktivnyy",
            specialty="Кардиолог",
            bio="Биография",
            is_active=True,
        )
        Doctor.objects.create(
            name="Неактивный врач",
            slug="neaktivnyy",
            specialty="Терапевт",
            bio="Биография",
            is_active=False,
        )

        url = reverse("doctors:doctor_list")
        response = client.get(url)

        assert len(response.context["doctors"]) == 1
        assert response.context["doctors"][0].name == "Активный врач"

    def test_doctor_list_pagination(self, client):
        """Тест пагинации списка врачей."""
        # Создаем 10 врачей (больше чем paginate_by=6)
        for i in range(10):
            Doctor.objects.create(
                name=f"Врач {i}",
                slug=f"doctor-{i}",
                specialty="Кардиолог",
                bio=f"Биография {i}",
                is_active=True,
            )

        url = reverse("doctors:doctor_list")
        response = client.get(url)

        assert response.status_code == 200
        assert "paginator" in response.context
        assert response.context["paginator"].count == 10
        assert len(response.context["doctors"]) == 6  # Первая страница

        # Проверяем вторую страницу
        response = client.get(url + "?page=2")
        assert response.status_code == 200
        assert len(response.context["doctors"]) == 4  # Вторая страница

    def test_doctor_list_search(self, client):
        """Тест поиска по врачам."""
        Doctor.objects.create(
            name="Иванов Иван",
            slug="ivanov",
            specialty="Кардиолог",
            bio="Опытный кардиолог",
            is_active=True,
        )
        Doctor.objects.create(
            name="Петров Петр",
            slug="petrov",
            specialty="Невролог",
            bio="Врач-невролог",
            is_active=True,
        )
        Doctor.objects.create(
            name="Сидоров Сидор",
            slug="sidorov",
            specialty="Хирург",
            bio="Хирург высшей категории",
            is_active=True,
        )

        # Поиск по имени
        url = reverse("doctors:doctor_list")
        response = client.get(url + "?q=Иванов")
        assert len(response.context["doctors"]) == 1
        assert response.context["doctors"][0].name == "Иванов Иван"

        # Поиск по специализации
        response = client.get(url + "?q=Невролог")
        assert len(response.context["doctors"]) == 1
        assert response.context["doctors"][0].name == "Петров Петр"

        # Поиск по био
        response = client.get(url + "?q=высшей категории")
        assert len(response.context["doctors"]) == 1
        assert response.context["doctors"][0].name == "Сидоров Сидор"

        # Поиск без результатов
        response = client.get(url + "?q=Несуществующий")
        assert len(response.context["doctors"]) == 0

    def test_doctor_list_filter_by_specialty(self, client):
        """Тест фильтрации по специализации."""
        Doctor.objects.create(
            name="Иванов Иван",
            slug="ivanov",
            specialty="Кардиолог",
            bio="Биография",
            is_active=True,
        )
        Doctor.objects.create(
            name="Петров Петр",
            slug="petrov",
            specialty="Невролог",
            bio="Биография",
            is_active=True,
        )
        Doctor.objects.create(
            name="Сидоров Сидор",
            slug="sidorov",
            specialty="Кардиолог",
            bio="Биография",
            is_active=True,
        )

        url = reverse("doctors:doctor_list")
        response = client.get(url + "?specialty=Кардиолог")

        assert len(response.context["doctors"]) == 2
        names = [d.name for d in response.context["doctors"]]
        assert "Иванов Иван" in names
        assert "Сидоров Сидор" in names
        assert response.context["current_specialty"] == "Кардиолог"

    def test_doctor_list_specialties_context(self, client):
        """Тест что в контекст передаются уникальные специализации."""
        Doctor.objects.create(
            name="Иванов Иван",
            slug="ivanov",
            specialty="Кардиолог",
            bio="Биография",
            is_active=True,
        )
        Doctor.objects.create(
            name="Петров Петр",
            slug="petrov",
            specialty="Невролог",
            bio="Биография",
            is_active=True,
        )
        Doctor.objects.create(
            name="Сидоров Сидор",
            slug="sidorov",
            specialty="Кардиолог",
            bio="Биография",
            is_active=True,
        )

        url = reverse("doctors:doctor_list")
        response = client.get(url)

        specialties = response.context["specialties"]
        assert len(specialties) == 2
        assert "Кардиолог" in specialties
        assert "Невролог" in specialties

    def test_doctor_list_search_query_in_context(self, client):
        """Тест что поисковый запрос передается в контекст."""
        url = reverse("doctors:doctor_list")
        response = client.get(url + "?q=тест")

        assert response.context["search_query"] == "тест"


@pytest.mark.django_db
class TestDoctorDetailView:
    """
    Тесты для детальной страницы врача.
    """

    def test_doctor_detail_view_get(self, client):
        """Тест GET запроса к детальной странице."""
        doctor = Doctor.objects.create(
            name="Иванов Иван",
            slug="ivanov-ivan",
            specialty="Кардиолог",
            bio="Подробная биография врача",
            experience_years=15,
            email="ivanov@example.com",
            phone="+7 (999) 123-45-67",
            is_active=True,
        )

        url = reverse("doctors:doctor_detail", args=[doctor.slug])
        response = client.get(url)

        assert response.status_code == 200
        assert "doctors/doctor_detail.html" in [t.name for t in response.templates]
        assert response.context["doctor"] == doctor
        assert "services" in response.context
        assert "appointments_count" in response.context

    def test_doctor_detail_inactive_doctor(self, client):
        """Тест что неактивный врач не отображается."""
        doctor = Doctor.objects.create(
            name="Иванов Иван",
            slug="ivanov-ivan",
            specialty="Кардиолог",
            bio="Биография",
            is_active=False,
        )

        url = reverse("doctors:doctor_detail", args=[doctor.slug])
        response = client.get(url)

        assert response.status_code == 404

    def test_doctor_detail_nonexistent_doctor(self, client):
        """Тест запроса к несуществующему врачу."""
        url = reverse("doctors:doctor_detail", args=["ne-sushestvuet"])
        response = client.get(url)

        assert response.status_code == 404

    def test_doctor_detail_with_services(self, client):
        """Тест отображения услуг врача."""
        doctor = Doctor.objects.create(
            name="Иванов Иван",
            slug="ivanov-ivan",
            specialty="Кардиолог",
            bio="Биография",
            is_active=True,
        )

        # Создаем услуги
        service1 = Service.objects.create(
            name="Услуга 1",
            slug="usluga-1",
            short_description="Описание 1",
            price=1000.00,
            duration=30,
            is_active=True,
        )
        service2 = Service.objects.create(
            name="Услуга 2",
            slug="usluga-2",
            short_description="Описание 2",
            price=2000.00,
            duration=45,
            is_active=True,
        )
        service3 = Service.objects.create(
            name="Неактивная услуга",
            slug="neaktivnaya",
            short_description="Описание",
            price=3000.00,
            duration=60,
            is_active=False,
        )

        # Добавляем услуги врачу
        doctor.services.add(service1, service2, service3)

        url = reverse("doctors:doctor_detail", args=[doctor.slug])
        response = client.get(url)

        # Должны отображаться только активные услуги
        assert len(response.context["services"]) == 2
        service_names = [s.name for s in response.context["services"]]
        assert "Услуга 1" in service_names
        assert "Услуга 2" in service_names
        assert "Неактивная услуга" not in service_names
