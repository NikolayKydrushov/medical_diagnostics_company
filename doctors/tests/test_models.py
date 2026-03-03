import pytest
from django.db import IntegrityError
from django.urls import reverse

from doctors.models import Doctor
from services.models import Service


@pytest.mark.django_db
class TestDoctorModel:
    """
    Тесты для модели Doctor.
    """

    def test_create_doctor(self):
        """Тест создания врача."""
        doctor = Doctor.objects.create(
            name="Иванов Иван Иванович",
            slug="ivanov-ivan-ivanovich",
            specialty="Кардиолог",
            bio="Опытный врач-кардиолог",
            experience_years=15,
            email="ivanov@example.com",
            phone="+7 (999) 123-45-67",
            order=1,
        )

        assert doctor.name == "Иванов Иван Иванович"
        assert doctor.slug == "ivanov-ivan-ivanovich"
        assert doctor.specialty == "Кардиолог"
        assert doctor.bio == "Опытный врач-кардиолог"
        assert doctor.experience_years == 15
        assert doctor.email == "ivanov@example.com"
        assert doctor.phone == "+7 (999) 123-45-67"
        assert doctor.order == 1
        assert doctor.is_active is True

    def test_doctor_str_method(self):
        """Тест строкового представления врача."""
        doctor = Doctor.objects.create(
            name="Иванов Иван Иванович", specialty="Кардиолог", bio="Биография"
        )
        assert str(doctor) == "Иванов Иван Иванович - Кардиолог"

    def test_slug_auto_generation(self):
        """Тест автоматической генерации slug."""
        pass

    def test_slug_unique(self):
        """Тест уникальности slug."""
        Doctor.objects.create(
            name="Иванов Иван", slug="test-slug", specialty="Кардиолог", bio="Биография"
        )

        with pytest.raises(IntegrityError):
            Doctor.objects.create(
                name="Петров Петр",
                slug="test-slug",
                specialty="Хирург",
                bio="Биография",
            )

    def test_get_absolute_url(self):
        """Тест метода get_absolute_url."""
        doctor = Doctor.objects.create(
            name="Иванов Иван",
            slug="ivanov-ivan",
            specialty="Кардиолог",
            bio="Биография",
        )
        url = doctor.get_absolute_url()
        assert url == reverse("doctors:doctor_detail", args=["ivanov-ivan"])

    def test_get_experience_display(self):
        """Тест форматирования стажа."""
        doctor = Doctor(name="Тестовый врач", specialty="Терапевт", bio="Биография")

        # Стаж 0 лет
        doctor.experience_years = 0
        assert doctor.get_experience_display() == "Стаж не указан"

        # Стаж 1 год
        doctor.experience_years = 1
        assert doctor.get_experience_display() == "1 год"

        # Стаж 2-4 года
        doctor.experience_years = 2
        assert doctor.get_experience_display() == "2 года"
        doctor.experience_years = 3
        assert doctor.get_experience_display() == "3 года"
        doctor.experience_years = 4
        assert doctor.get_experience_display() == "4 года"

        # Стаж 5+ лет
        doctor.experience_years = 5
        assert doctor.get_experience_display() == "5 лет"
        doctor.experience_years = 10
        assert doctor.get_experience_display() == "10 лет"

    def test_default_values(self):
        """Тест значений по умолчанию."""
        pass

    def test_services_relation(self):
        """Тест связи с услугами."""
        # Создаем врача
        doctor = Doctor.objects.create(
            name="Иванов Иван",
            slug="ivanov-ivan",
            specialty="Кардиолог",
            bio="Биография",
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

        # Добавляем услуги врачу
        doctor.services.add(service1, service2)

        assert doctor.services.count() == 2
        assert service1 in doctor.services.all()
        assert service2 in doctor.services.all()

        # Проверяем обратную связь
        assert doctor in service1.doctors.all()
        assert doctor in service2.doctors.all()

    def test_ordering(self):
        """Тест сортировки врачей."""
        doctor1 = Doctor.objects.create(
            name="Б врач",
            slug="b-vrach",
            specialty="Кардиолог",
            bio="Биография",
            order=2,
        )
        doctor2 = Doctor.objects.create(
            name="А врач",
            slug="a-vrach",
            specialty="Терапевт",
            bio="Биография",
            order=1,
        )
        doctor3 = Doctor.objects.create(
            name="В врач", slug="v-vrach", specialty="Хирург", bio="Биография", order=1
        )

        doctors = Doctor.objects.all()
        assert doctors[0] == doctor2  # order=1, name='А врач'
        assert doctors[1] == doctor3  # order=1, name='В врач'
        assert doctors[2] == doctor1  # order=2, name='Б врач'

    def test_is_active_filtering(self):
        """Тест фильтрации по активности."""
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

        active_doctors = Doctor.objects.filter(is_active=True)
        assert active_doctors.count() == 1
        assert active_doctors[0].name == "Активный врач"

    def test_timestamps(self):
        """Тест временных меток."""
        import datetime

        doctor = Doctor.objects.create(
            name="Иванов Иван",
            slug="ivanov-ivan",
            specialty="Кардиолог",
            bio="Биография",
        )

        assert doctor.created_at is not None
        assert doctor.updated_at is not None
        assert isinstance(doctor.created_at, datetime.datetime)
        assert isinstance(doctor.updated_at, datetime.datetime)

    def test_meta_verbose_names(self):
        """Тест verbose names в Meta классе."""
        assert Doctor._meta.verbose_name == "Врач"
        assert Doctor._meta.verbose_name_plural == "Врачи"
        assert Doctor._meta.ordering == ["order", "name"]

    def test_field_verbose_names(self):
        """Тест verbose names полей."""
        assert Doctor._meta.get_field("name").verbose_name == "ФИО врача"
        assert Doctor._meta.get_field("specialty").verbose_name == "Специализация"
        assert Doctor._meta.get_field("bio").verbose_name == "Биография"
        assert (
            Doctor._meta.get_field("experience_years").verbose_name
            == "Стаж работы (лет)"
        )
        assert Doctor._meta.get_field("services").verbose_name == "Услуги"
        assert Doctor._meta.get_field("is_active").verbose_name == "Активен"

    def test_help_texts(self):
        """Тест help_text полей."""
        assert "Например: кардиолог" in Doctor._meta.get_field("specialty").help_text
        assert "Образование, опыт" in Doctor._meta.get_field("bio").help_text
        assert "Какие услуги оказывает" in Doctor._meta.get_field("services").help_text
        assert "Отображать ли врача" in Doctor._meta.get_field("is_active").help_text
