import pytest
from django.test import Client
from django.urls import reverse

from services.models import Service


@pytest.mark.django_db
class TestServiceListView:
    """
    Тесты для списка услуг.
    """

    def test_service_list_view_get(self, client):
        """Тест GET запроса к списку услуг."""
        url = reverse("services:service_list")
        response = client.get(url)

        assert response.status_code == 200
        assert "services/service_list.html" in [t.name for t in response.templates]
        assert "services" in response.context
        assert "search_query" in response.context

    def test_service_list_pagination(self, client):
        """Тест пагинации списка услуг."""
        # Создаем 10 услуг (больше чем paginate_by=9)
        for i in range(10):
            Service.objects.create(
                name=f"Услуга {i}",
                slug=f"usluga-{i}",
                short_description=f"Описание {i}",
                price=1000.00 + i,
                duration=30,
                is_active=True,
            )

        url = reverse("services:service_list")
        response = client.get(url)

        assert response.status_code == 200
        assert "paginator" in response.context
        assert response.context["paginator"].count == 10
        assert len(response.context["services"]) == 9  # Первая страница

        # Проверяем вторую страницу
        response = client.get(url + "?page=2")
        assert response.status_code == 200
        assert len(response.context["services"]) == 1  # Вторая страница

    def test_service_list_only_active(self, client):
        """Тест что отображаются только активные услуги."""
        # Создаем активные и неактивные услуги
        Service.objects.create(
            name="Активная услуга 1",
            slug="aktivnaya-1",
            short_description="Описание",
            price=1000.00,
            duration=30,
            is_active=True,
        )
        Service.objects.create(
            name="Активная услуга 2",
            slug="aktivnaya-2",
            short_description="Описание",
            price=2000.00,
            duration=45,
            is_active=True,
        )
        Service.objects.create(
            name="Неактивная услуга",
            slug="neaktivnaya",
            short_description="Описание",
            price=3000.00,
            duration=60,
            is_active=False,
        )

        url = reverse("services:service_list")
        response = client.get(url)

        assert response.status_code == 200
        assert len(response.context["services"]) == 2
        names = [s.name for s in response.context["services"]]
        assert "Активная услуга 1" in names
        assert "Активная услуга 2" in names
        assert "Неактивная услуга" not in names

    def test_service_list_search(self, client):
        """Тест поиска по услугам."""
        Service.objects.create(
            name="МРТ головного мозга",
            slug="mrt",
            short_description="МРТ исследование",
            full_description="Подробно о МРТ",
            price=5000.00,
            duration=30,
            is_active=True,
        )
        Service.objects.create(
            name="УЗИ брюшной полости",
            slug="uzi",
            short_description="УЗИ диагностика",
            full_description="Подробно об УЗИ",
            price=2500.00,
            duration=20,
            is_active=True,
        )
        Service.objects.create(
            name="Рентген",
            slug="rentgen",
            short_description="Рентгенография",
            full_description="Рентген легких",
            price=1500.00,
            duration=10,
            is_active=True,
        )

        # Поиск по названию
        url = reverse("services:service_list")
        response = client.get(url + "?q=МРТ")
        assert response.status_code == 200
        assert len(response.context["services"]) == 1
        assert response.context["services"][0].name == "МРТ головного мозга"

        # Поиск по краткому описанию
        response = client.get(url + "?q=УЗИ")
        assert response.status_code == 200
        assert len(response.context["services"]) == 1
        assert response.context["services"][0].name == "УЗИ брюшной полости"

        # Поиск по полному описанию
        response = client.get(url + "?q=Рентген")
        assert response.status_code == 200
        assert len(response.context["services"]) == 1
        assert response.context["services"][0].name == "Рентген"

        # Поиск без результатов
        response = client.get(url + "?q=Несуществующий")
        assert response.status_code == 200
        assert len(response.context["services"]) == 0

    def test_service_list_search_query_in_context(self, client):
        """Тест что поисковый запрос передается в контекст."""
        url = reverse("services:service_list")
        response = client.get(url + "?q=тест")

        assert response.status_code == 200
        assert response.context["search_query"] == "тест"

    def test_service_list_ordering(self, client):
        """Тест сортировки услуг."""
        Service.objects.create(
            name="Б услуга",
            slug="b",
            short_description="Описание",
            price=2000.00,
            duration=30,
            order=2,
            is_active=True,
        )
        Service.objects.create(
            name="А услуга",
            slug="a",
            short_description="Описание",
            price=1000.00,
            duration=30,
            order=1,
            is_active=True,
        )
        Service.objects.create(
            name="В услуга",
            slug="v",
            short_description="Описание",
            price=3000.00,
            duration=30,
            order=1,
            is_active=True,
        )

        url = reverse("services:service_list")
        response = client.get(url)

        services = response.context["services"]
        assert services[0].name == "А услуга"  # order=1, name='А услуга'
        assert services[1].name == "В услуга"  # order=1, name='В услуга'
        assert services[2].name == "Б услуга"  # order=2


@pytest.mark.django_db
class TestServiceDetailView:
    """
    Тесты для детальной страницы услуги.
    """

    def test_service_detail_view_get(self, client):
        """Тест GET запроса к детальной странице."""
        service = Service.objects.create(
            name="Тестовая услуга",
            slug="test-service",
            short_description="Описание",
            full_description="Полное описание",
            price=1000.00,
            duration=30,
            is_active=True,
        )

        url = reverse("services:service_detail", args=[service.slug])
        response = client.get(url)

        assert response.status_code == 200
        assert "services/service_detail.html" in [t.name for t in response.templates]
        assert response.context["service"] == service
        assert "doctors" in response.context
        assert "related_services" in response.context

    def test_service_detail_inactive_service(self, client):
        """Тест что неактивная услуга не отображается."""
        service = Service.objects.create(
            name="Неактивная услуга",
            slug="inactive",
            short_description="Описание",
            price=1000.00,
            duration=30,
            is_active=False,
        )

        url = reverse("services:service_detail", args=[service.slug])
        response = client.get(url)

        assert response.status_code == 404  # Должен быть 404 Not Found

    def test_service_detail_nonexistent_service(self, client):
        """Тест запроса к несуществующей услуге."""
        url = reverse("services:service_detail", args=["ne-sushestvuet"])
        response = client.get(url)

        assert response.status_code == 404

    def test_service_detail_context_data(self, client):
        """Тест контекстных данных детальной страницы."""
        service = Service.objects.create(
            name="Тестовая услуга",
            slug="test-service",
            short_description="Описание",
            full_description="Полное описание",
            price=1000.00,
            duration=30,
            is_active=True,
        )

        # Создаем еще несколько услуг для "похожих"
        for i in range(5):
            Service.objects.create(
                name=f"Похожая услуга {i}",
                slug=f"pohozhaya-{i}",
                short_description=f"Описание {i}",
                price=1000.00 + i,
                duration=30,
                is_active=True,
            )

        url = reverse("services:service_detail", args=[service.slug])
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["service"] == service
        assert "doctors" in response.context
        assert "related_services" in response.context
        assert (
            len(response.context["related_services"]) == 3
        )  # Должно быть 3 похожих услуги
        assert service not in response.context["related_services"]  # Исключаем текущую

    @pytest.mark.skip(reason="Требуется создание врачей")
    def test_service_detail_with_doctors(self, client):
        """Тест отображения врачей для услуги."""
        # Будет реализовано после создания тестов для doctors
        pass
