from django.db.models import Q
from django.views.generic import DetailView, ListView
from .models import Service

# Create your views here.


class ServiceListView(ListView):
    """
    Представление для списка всех услуг.
    Поддерживает поиск и фильтрацию.
    """

    model = Service
    template_name = "services/service_list.html"
    context_object_name = "services"
    paginate_by = 9  # Показываем по 9 услуг на странице

    def get_queryset(self):
        """
        Фильтруем услуги: только активные, с сортировкой.
        Добавляем поиск по названию и описанию.
        """
        queryset = Service.objects.filter(is_active=True).order_by("order", "name")

        # Поиск по GET-параметру 'q'
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query)
                | Q(short_description__icontains=query)
                | Q(full_description__icontains=query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем поисковый запрос в контекст для отображения в шаблоне
        context["search_query"] = self.request.GET.get("q", "")
        return context


class ServiceDetailView(DetailView):
    """
    Представление для детальной страницы услуги.
    """

    model = Service
    template_name = "services/service_detail.html"
    context_object_name = "service"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        """Показываем только активные услуги."""
        return Service.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем врачей, которые оказывают эту услугу
        context["doctors"] = self.object.doctors.filter(is_active=True)

        # Похожие услуги (по категории или просто случайные)
        context["related_services"] = Service.objects.filter(is_active=True).exclude(
            id=self.object.id
        )[:3]

        return context
