import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from pages.models import AboutPageContent, HomePageContent


@pytest.mark.django_db
class TestHomePageContentModel:
    """
    Тесты для модели HomePageContent.
    """

    def test_create_home_content(self):
        """Тест создания контента главной страницы."""
        content = HomePageContent.objects.create(
            hero_title="Тестовый заголовок",
            hero_subtitle="Тестовый подзаголовок",
            about_title="О тестовом центре",
            about_text="Текст о тестовом центре",
            advantages=[{"title": "Преимущество 1", "description": "Описание 1"}],
            patients_count=1000,
            doctors_count=50,
            experience_years=10,
            meta_title="Meta Title",
            meta_description="Meta Description",
        )

        assert content.hero_title == "Тестовый заголовок"
        assert content.hero_subtitle == "Тестовый подзаголовок"
        assert content.about_title == "О тестовом центре"
        assert content.about_text == "Текст о тестовом центре"
        assert content.advantages == [
            {"title": "Преимущество 1", "description": "Описание 1"}
        ]
        assert content.patients_count == 1000
        assert content.doctors_count == 50
        assert content.experience_years == 10
        assert content.meta_title == "Meta Title"
        assert content.meta_description == "Meta Description"

    def test_home_content_str_method(self):
        """Тест строкового представления."""
        content = HomePageContent.objects.create(
            hero_title="Заголовок",
            hero_subtitle="Подзаголовок",
            about_title="О компании",
            about_text="Текст",
        )
        assert str(content) == "Главная страница"

    def test_home_content_default_values(self):
        """Тест значений по умолчанию."""
        content = HomePageContent.objects.create(about_text="Текст о компании")

        assert content.hero_title == "Медицинский диагностический центр"
        assert content.hero_subtitle == "Современное оборудование и опытные врачи"
        assert content.about_title == "О нашем центре"
        assert content.patients_count == 0
        assert content.doctors_count == 0
        assert content.experience_years == 0
        assert content.advantages == []
        assert content.meta_title == ""
        assert content.meta_description == ""

    def test_home_content_singleton(self):
        """Тест синглтона - нельзя создать вторую запись."""
        HomePageContent.objects.create(about_text="Первая запись")

        # Пытаемся создать вторую запись
        with pytest.raises(ValidationError):
            HomePageContent.objects.create(about_text="Вторая запись")

    def test_home_content_advantages_json(self):
        """Тест JSON поля для преимуществ."""
        advantages = [
            {"title": "Преимущество 1", "description": "Описание 1"},
            {"title": "Преимущество 2", "description": "Описание 2"},
        ]
        content = HomePageContent.objects.create(
            about_text="Текст", advantages=advantages
        )

        assert content.advantages == advantages
        assert len(content.advantages) == 2
        assert content.advantages[0]["title"] == "Преимущество 1"

    def test_home_content_updated_at(self):
        """Тест обновления временной метки."""
        import datetime

        from django.utils import timezone

        content = HomePageContent.objects.create(about_text="Текст")
        assert content.updated_at is not None

        old_updated = content.updated_at
        content.hero_title = "Новый заголовок"
        content.save()
        content.refresh_from_db()
        assert content.updated_at > old_updated

    def test_home_content_meta_verbose_names(self):
        """Тест verbose names."""
        assert HomePageContent._meta.verbose_name == "Контент главной страницы"
        assert HomePageContent._meta.verbose_name_plural == "Контент главной страницы"

    def test_home_content_field_verbose_names(self):
        """Тест verbose names полей."""
        assert (
            HomePageContent._meta.get_field("hero_title").verbose_name
            == "Заголовок главного баннера"
        )
        assert (
            HomePageContent._meta.get_field("hero_subtitle").verbose_name
            == "Подзаголовок"
        )
        assert (
            HomePageContent._meta.get_field("about_title").verbose_name
            == "Заголовок раздела 'О компании'"
        )
        assert (
            HomePageContent._meta.get_field("patients_count").verbose_name
            == "Количество пациентов"
        )
        assert (
            HomePageContent._meta.get_field("doctors_count").verbose_name
            == "Количество врачей"
        )


@pytest.mark.django_db
class TestAboutPageContentModel:
    """
    Тесты для модели AboutPageContent.
    """

    def test_create_about_content(self):
        """Тест создания контента страницы 'О компании'."""
        content = AboutPageContent.objects.create(
            title="О компании",
            history_title="Наша история",
            history_text="Текст истории",
            mission_title="Наша миссия",
            mission_text="Текст миссии",
            values_title="Наши ценности",
            values=[{"title": "Ценность 1", "description": "Описание 1"}],
            equipment_title="Оборудование",
            equipment_description="Описание оборудования",
            meta_title="Meta Title",
            meta_description="Meta Description",
        )

        assert content.title == "О компании"
        assert content.history_title == "Наша история"
        assert content.history_text == "Текст истории"
        assert content.mission_title == "Наша миссия"
        assert content.mission_text == "Текст миссии"
        assert content.values_title == "Наши ценности"
        assert content.values == [{"title": "Ценность 1", "description": "Описание 1"}]
        assert content.equipment_title == "Оборудование"
        assert content.equipment_description == "Описание оборудования"
        assert content.meta_title == "Meta Title"
        assert content.meta_description == "Meta Description"

    def test_about_content_str_method(self):
        """Тест строкового представления."""
        content = AboutPageContent.objects.create(
            history_text="История", mission_text="Миссия"
        )
        assert str(content) == "Страница 'О компании'"

    def test_about_content_default_values(self):
        """Тест значений по умолчанию."""
        content = AboutPageContent.objects.create(
            history_text="История", mission_text="Миссия"
        )

        assert content.title == "О компании"
        assert content.history_title == "Наша история"
        assert content.mission_title == "Наша миссия"
        assert content.values_title == "Наши ценности"
        assert content.equipment_title == "Наше оборудование"
        assert content.equipment_description == ""
        assert content.values == []
        assert content.meta_title == ""
        assert content.meta_description == ""

    def test_about_content_singleton(self):
        """Тест синглтона - нельзя создать вторую запись."""
        AboutPageContent.objects.create(
            history_text="Первая запись", mission_text="Миссия"
        )

        # Пытаемся создать вторую запись
        with pytest.raises(ValidationError):
            AboutPageContent.objects.create(
                history_text="Вторая запись", mission_text="Миссия"
            )

    def test_about_content_values_json(self):
        """Тест JSON поля для ценностей."""
        values = [
            {"title": "Ценность 1", "description": "Описание 1"},
            {"title": "Ценность 2", "description": "Описание 2"},
        ]
        content = AboutPageContent.objects.create(
            history_text="История", mission_text="Миссия", values=values
        )

        assert content.values == values
        assert len(content.values) == 2
        assert content.values[0]["title"] == "Ценность 1"

    def test_about_content_updated_at(self):
        """Тест обновления временной метки."""
        content = AboutPageContent.objects.create(
            history_text="История", mission_text="Миссия"
        )
        assert content.updated_at is not None

        old_updated = content.updated_at
        content.title = "Новый заголовок"
        content.save()
        content.refresh_from_db()
        assert content.updated_at > old_updated

    def test_about_content_meta_verbose_names(self):
        """Тест verbose names."""
        assert AboutPageContent._meta.verbose_name == "Контент страницы 'О компании'"
        assert (
            AboutPageContent._meta.verbose_name_plural
            == "Контент страницы 'О компании'"
        )

    def test_about_content_required_fields(self):
        """Тест обязательных полей."""
        # Должно работать с минимальными полями
        content = AboutPageContent.objects.create(
            history_text="История", mission_text="Миссия"
        )
        assert content.history_text == "История"
        assert content.mission_text == "Миссия"

        # Без обязательных полей не должно работать
        with pytest.raises(Exception):
            AboutPageContent.objects.create()
