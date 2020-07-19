from django.db.models import F
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.views.generic import CreateView, ListView, DetailView

from restaurants.forms import LoginForm
from restaurants.models import Client, Restaurant, RestaurantRating


class BaseClientInSessionMixin:
    def get(self, request, *args, **kwargs):
        if not self.request.session.get('client'):
            return redirect('login')
        else:
            return super().get(request, *args, **kwargs)


class LoginView(CreateView):
    form_class = LoginForm
    template_name = 'login.html'

    def form_valid(self, form):
        client, _ = Client.objects.get_or_create(**form.cleaned_data)
        self.request.session['client'] = client.name
        return redirect('restaurants')


class RestaurantsView(BaseClientInSessionMixin, ListView):
    model = Restaurant
    template_name = 'restaurants.html'
    paginate_by = 10
    queryset = Restaurant.objects.all().order_by('id')

    def get(self, request, *args, **kwargs):
        """This view return list of all restaurants or only the searched ones when request is AJAX"""
        if request.is_ajax() and request.GET.get('term'):
            restaurants = self.get_queryset().filter(name__icontains=request.GET.get('term')).annotate(label=F('name'))
            data = list(restaurants.values('label', 'id'))
            return JsonResponse(data, safe=False)
        return super().get(request, *args, **kwargs)


class RestaurantDetailView(BaseClientInSessionMixin, DetailView):
    """This view has GET method for retrieving Restaurant data and AJAX POST method for adding rating"""
    model = Restaurant
    template_name = 'restaurant_detail.html'

    def post(self, request, *args, **kwargs):
        if self.request.is_ajax():
            value = request.POST.get('value')
            if type(value) == str and value.isdigit() and 0 < int(value) < 6:
                if Client.objects.filter(name=self.request.session.get('client')):
                    RestaurantRating.objects.create(
                        restaurant=self.get_object(),
                        rating=int(value),
                        client=Client.objects.get(name=self.request.session['client'])
                    )
                    return JsonResponse({'msg': "Rating added"}, safe=False, status=201)
                return JsonResponse({'msg': "Invalid client in session"}, safe=False, status=400)
            return JsonResponse({'msg': "Invalid value"}, safe=False, status=400)
        return HttpResponse('This endpoint accepts only AJAX POSTs', status=400)
