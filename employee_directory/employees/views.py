from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, DeleteView, UpdateView

from employees.forms import EmployeeCreateForm, EmployeeEditForm
from employees.models import Employee


class EmployeeTreeView(TemplateView):
    template_name = ".employees/employees_tree.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {"root_employees": Employee.objects.filter(level=0)}


class EmployeeTreeViewGetChildren(TemplateView):
    template_name = ".employees/employees_tree_children.html"

    def get_context_data(self, **kwargs):
        parent_pk = self.request.GET.get("parent_pk")
        return super().get_context_data(**kwargs) | {"children": Employee.objects.filter(parent_id=parent_pk)}


class EmployeeListView(LoginRequiredMixin, ListView):
    raise_exception = False  # Отключаем ошибку. С этим флагом вместо ошибки будет переадресация на settings.LOGIN_URL
    template_name = '.employees/employees_list.html'  # указываем шаблон
    ordering = '-pk'  # опциональный и работает даже если get_queryset не переопределять
    model = Employee  # указывается для ListView (обязательный)
    per_page: int = 5  # количество объектов на странице
    available_per_page_range = [5, 10, 20, 30, 50]  # доступный per_page

    def get_queryset(self):
        qs = super().get_queryset()  # получаем queryset от родителя (ListView).
        search_query = self.request.GET.get('search')  # Получаем параметр поиска из запроса GET
        if search_query:
            qs = qs.filter(  # Ищем, если есть запрос
                Q(name__icontains=search_query) |
                Q(position__icontains=search_query) |
                Q(date_of_receipt__icontains=search_query) |
                Q(salary__icontains=search_query)
            )
        # Получаем параметр сортировки из запроса GET или используем тот, что по умолчанию
        order_by = self.request.GET.get('sort_by', self.ordering)
        return qs.order_by(order_by)

    def get_context_data(self, *args, **kwargs):
        # вызываем родительский метод, чтоб не потерять контекст от ListView
        context = super().get_context_data(*args, **kwargs)
        request_data = self.request.GET

        # проверяем, не запрашивали ли другой диапазон
        per_page = request_data.get('per_page', self.per_page)
        try:
            per_page = int(per_page)  # валидируем на то, что нам передали число в query параметре
        except ValueError:
            per_page = self.per_page
        if per_page not in self.available_per_page_range:  # проверяем, что мы разрешаем столько запрашивать
            per_page = self.per_page
        # получаем список объектов из контекста (get_queryset возвращает как раз object_list
        queryset = context['object_list']
        paginator = Paginator(queryset, per_page)  # инициализируем пагинатор
        page_number = request_data.get('page', 1)  # получаем номер страницы из запроса
        page_object = paginator.get_page(page_number)

        # Скрываем лишние страницы (1, 2, 3 ... 99, 100)
        page_object.adjusted_elided_pages = paginator.get_elided_page_range(page_number)
        return context | {"search_query": request_data.get('search'),  # Добавляем параметры из запроса
                          "sort_by": request_data.get('sort_by'),
                          "page_obj": page_object,  # и объект пагинатора
                          "available_per_page_range": self.available_per_page_range,
                          "per_page_value": per_page}


class EmployeeCreateView(LoginRequiredMixin, CreateView):
    raise_exception = False
    template_name = ".employees/create_employee.html"
    form_class = EmployeeCreateForm
    success_url = reverse_lazy('employees:employees_list')  # url для редиректа при успешной обработке формы


class EmployeeDeleteView(LoginRequiredMixin, DeleteView):
    raise_exception = False
    model = Employee
    template_name = ".employees/delete_employee.html"
    success_url = reverse_lazy('employees:employees_list')  # url для редиректа при успешной обработке формы


class EmployeeUpdateView(LoginRequiredMixin, UpdateView):
    raise_exception = False
    model = Employee
    form_class = EmployeeEditForm
    template_name = '.employees/edit_employee.html'
    success_url = reverse_lazy('employees:employees_list')
