from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('home', views.home, name='home'),
    path('', views.signin, name='signin'),
    path('signup', views.signup, name='signup'),
    path('log-out', views.userlogout, name='userlogout'),
    path('add_package/', views.add_package, name='add_package'),
    path('update_package/<int:id>/', views.update_package, name='update_package'),


    path('packages', views.packages, name='packages'),
    path('aboutus', views.aboutus, name='aboutus'),
    path('booknow', views.booknow, name='booknow'),
    path('viewpackagedetails/<int:id>', views.viewpackagedetails, name='viewpackagedetails'),
    path('bookings/<id>', views.bookings, name='bookings'),
    path(' /<id>', views.booking_review, name='booking_revi'),
    path('profile/create/', views.profile_create, name='profile_create'),  # Add this line
    path('confirm/<id>', views.confirm_booking, name='confirm_booking'),
    path('my_bookings', views.my_bookings, name='my_bookings'),
    path('vehicle_list1/', views.vehicle_list1, name='vehicle_list1'),


    ####################################################################################################3
    path('admin',views.admin, name='admin'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    # path('addpackages/',views.addpackages,name='addpackages'),
    path('vehicles/',views.vehicles,name='vehicles'),
    path('checkout/<int:package_id>/<int:vehicle_id>/', views.checkout, name='checkout'),
    path('delete-package/<int:id>/', views.delete_package, name='delete_package'),




    path('bookings/', views.booking_list, name='booking_list'),
    path('customers/', views.customer_list, name='customer_list'),
    path('packages/', views.package_list, name='package_list'),
    path('reviews/', views.review_list, name='review_list'),
    path('vehicles/', views.vehicle_list, name='vehicle_list'),

    #####payments###
    path('book/<int:package_id>/', views.create_booking, name='create_booking'),
    path('payment-success/<int:booking_id>/', views.payment_success, name='payment_success'), 
    path('view_bookings', views.view_bookings, name='view_bookings'),
       
]

    




if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)