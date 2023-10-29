from . import views
from django.urls import path
from ecommerce import settings
from django.conf.urls.static import static
urlpatterns = [
    path('',views.index,name='index'),
    path('dashboard',views.dashboard,name='dashboard'),
    path('submit',views.submit,name='submit'),
    path('register',views.register,name='register'),
    path('details/<int:id>/',views.details,name='details'),
    path('contact',views.contact,name='contact'),
    path('profile',views.profile,name="profile"),
    path('logout',views.log_out,name='logout'),
    path('addCart',views.addCart,name='addCart'),
    path('showCart',views.showCart,name='showCart'),
    path('quantity',views.quantity,name='quantity'),
    path('remove',views.remove,name='remove'),
    path('checkout',views.checkout,name='checkout'),
    path('payment',views.payment,name="payment"),
    path('wishlist',views.showlist,name='showlist'),
    path('addwish', views.addwish, name='addwish'),
    path('order',views.order,name='order'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
