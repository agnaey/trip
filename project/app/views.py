from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import *
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib import messages
from datetime import datetime
import razorpay



      
def signin(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            request.session['username'] = username
            if  user.is_superuser:
                return redirect('admin')
            else:
                return redirect('home')
        else:
            messages.error(request, "Invalid credentials.")
    
    return render(request, 'signin.html')
def signup(request):
    if request.method == 'POST':  
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confirmpassword')

        if not username or not email or not password or not confirmpassword:
            messages.error(request, 'All fields are required.')
        elif confirmpassword != password:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            # Corrected line to use create_user
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, "Account created successfully!")
            return redirect('signin')  

    return render(request, "signup.html")


def userlogout(request):
    request.session.flush()
    return render(request, 'home.html')

# ---------------------------------------------------------------------

def home(request):
    vehicles = Vehicle.objects.all()
    packages = Package.objects.all()[:3]  # Show latest 6 packages on homepage
    reviews = Review.objects.all()  # All reviews for testimonials
    context = {
    'Packages': packages,
    'Reviews': reviews,
    'vehicles': vehicles,
    }
    return render(request,'home.html',context)


def add_package(request):
    if request.method == 'POST':
        title = request.POST['title']
        duration_days = request.POST['duration_days']
        description = request.POST['description']
        included = request.POST['included']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        image = request.FILES.get('image')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')

        Package.objects.create(
            title=title,
            duration_days=duration_days,
            description=description,
            included=included,
            start_date=start_date,
            end_date=end_date,
            image=image,
            image2=image2,
            image3=image3,
        )
        return redirect('admin')  

    return render(request, 'admin/add_package.html')

def update_package(request, id):
    package = get_object_or_404(Package, id=id)

    if request.method == 'POST':
        package.title = request.POST['title']
        package.duration_days = request.POST['duration_days']
        package.description = request.POST['description']
        package.included = request.POST['included']
        package.start_date = request.POST['start_date']
        package.end_date = request.POST['end_date']

        if 'image' in request.FILES:
            package.image = request.FILES['image']
        if 'image2' in request.FILES:
            package.image2 = request.FILES['image2']
        if 'image3' in request.FILES:
            package.image3 = request.FILES['image3']

        package.save()
        return redirect('admin')

    return render(request, 'admin/update_package.html', {'package': package})





def viewpackagedetails(request, id):
    package = get_object_or_404(Package, id=id)
    # Get related packages (you can customize this query as needed)
    related_packages = Package.objects.exclude(id=id).order_by('-start_date')[:3]
    context = {
        'package': package,
        'related_packages': related_packages
    }
    return render(request, 'viewpackagedetails.html', context)
def bookings(request, id):  # id = Package id
    package = get_object_or_404(Package, id=id)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        checkin = request.POST.get('checkin')
        checkout = request.POST.get('checkout')
        guests = request.POST.get('guests')
        message = request.POST.get('message')

        # For demo, assume number_of_people is parsed from `guests`
        number_of_people = 1 if guests == "1" else 2 if guests == "2" else 4 if guests == "3-4" else 5

        customer = Customer.objects.get(user=request.user)

        booking = Booking.objects.create(
            customer=customer,
            travel_package=package,
            number_of_people=number_of_people,
            total_price=number_of_people * package.price,
            status='Pending'
        )

        return redirect('booking_revi', id=package.id)  # or wherever you want to go after

    return render(request, 'bookings.html', {'package': package})


def booking_review(request, id):  # id = Package id
    package = get_object_or_404(Package, id=id)

    if request.method == 'POST':
        # Check if the customer exists
        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            # If no customer profile exists, show an error message
            messages.error(request, 'You need to create a customer profile before making a booking.')
            return redirect('profile_create')  # Redirect to the profile creation page (you need to create this view)

        # Extract form data
        number_of_people = request.POST.get('guests')

        if not number_of_people or not number_of_people.isdigit() or int(number_of_people) <= 0:
            messages.error(request, 'Please enter a valid number of guests.')
            return redirect('booking_review', id=id)

        # Calculate total price based on number of people
        total_price = int(number_of_people) * package.price

        # Create a temporary booking object or simply pass this data to the confirmation page
        context = {
            'package': package,
            'number_of_people': number_of_people,
            'total_price': total_price,
        }
        return render(request, 'booking_confirm.html', context)

    return render(request, 'booking_review.html', {'package': package})

def profile_create(request):
    if request.method == 'POST':
        # Get the form data manually from the request
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        # Check if data is provided
        if not phone or not address:
            messages.error(request, "Both phone and address are required.")
            return redirect('profile_create')

        # Create and save the customer profile
        try:
            customer = Customer.objects.create(user=request.user, phone=phone, address=address)
            customer.save()
            messages.success(request, "Profile created successfully.")
            return redirect('home')  # Redirect after successful profile creation
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('profile_create')
    
    return render(request, 'profile.html')

def confirm_booking(request, id):  # id = Package id
    package = get_object_or_404(Package,id=id)

    if request.method == 'POST':
        # Check if the customer exists
        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            messages.error(request, 'You need to create a customer profile before confirming the booking.')
            return redirect('profile_create')  # Redirect to the profile creation page

        # Extract form data from the session or POST
        number_of_people = request.POST.get('guests')
        total_price = int(number_of_people) * package.price

        # Create a new booking object
        booking = Booking.objects.create(
            customer=customer,
            package=package,
            number_of_people=number_of_people,
            total_price=total_price,
            status='Confirmed',  # Mark as confirmed
        )

        messages.success(request, 'Your booking has been confirmed successfully!')
        return redirect('my_bookings')  # Redirect to a success page

    return render(request, 'booking_confirm.html', {'package': package})

def my_bookings(request):
    # Ensure the user is logged in
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login page if the user is not authenticated
    try:
        # Get the customer's profile
        customer = request.user.customer  # Assuming each user has a corresponding Customer profile
    except Customer.DoesNotExist:
        # If no customer profile exists, show an error message
        messages.error(request, 'You need to create a customer profile to view your bookings.')
        return redirect('profile_create')  # Redirect to profile creation page

    # Retrieve all bookings for the logged-in customer
    bookings = Booking.objects.filter(customer=customer)

    return render(request, 'my_bookings.html', {'bookings': bookings})


def add_vehicle_admin(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        package_id = request.POST.get('package')
        price = request.POST.get('price')
        
        try:
            package = Package.objects.get(id=package_id)
            vehicle = Vehicle(name=name, package=package, price=price)
            vehicle.save()
            messages.success(request, 'Vehicle added successfully!')
            return redirect('/admin/vehicles/')  # Redirect to vehicles list
        except Exception as e:
            messages.error(request, f'Error adding vehicle: {str(e)}')
            
    packages = Package.objects.all()
    context = {
        'packages': packages,
    }
    return render(request, 'add_vehicle_admin.html', context)



# def addpackages(request):
#     if request.method == 'POST':
#         try:
#             # Extract form data
#             title = request.POST.get('title')
#             duration_days = request.POST.get('duration_days')
#             description = request.POST.get('description')
#             included = request.POST.get('included')
#             start_date = request.POST.get('start_date')
#             end_date = request.POST.get('end_date')
            
#             # Create new package object
#             package = Package(
#                 title=title,
#                 duration_days=duration_days,
#                 description=description,
#                 included=included,
#                 start_date=start_date,
#                 end_date=end_date
#             )
            
#             # Handle image uploads
#             if 'image' in request.FILES:
#                 package.image = request.FILES['image']
            
#             if 'image2' in request.FILES:
#                 package.image2 = request.FILES['image2']
            
#             if 'image3' in request.FILES:
#                 package.image3 = request.FILES['image3']
            
#             # Save package to database
#             package.save()
            
#             messages.success(request, f'Package "{title}" added successfully!')
#             return redirect('/admin/packages/')  # Redirect to packages list
#         except Exception as e:
#             messages.error(request, f'Error adding package: {str(e)}')
    
#     return render(request, 'admin/addpackages.html')



def vehicles(request):
    vehicles = Vehicle.objects.all()
    return render(request, 'vehicles.html', {'vehicles': vehicles})

def packages(request):
    packages = Package.objects.all()
    return render(request,'packages.html',{'packages':packages})
def aboutus(request):
    return render(request,'aboutus.html')

def booknow(request):
    return render(request,'booknow.html')    


def admin(request):
    return render(request,'admin/admin.html')




def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer__user=request.user)
    booking.status = 'Cancelled'
    booking.save()
    return redirect('my_bookings')

    ######################################admin##########################################

def booking_list(request):
    bookings = Booking.objects.select_related('customer', 'travel_package')
    return render(request, 'admin/booking_list.html', {'bookings': bookings})

def customer_list(request):
    customers = Customer.objects.select_related('user')
    return render(request, 'admin/customer_list.html', {'customers': customers})

def package_list(request):
    packages = Package.objects.all()
    return render(request, 'admin/package_list.html', {'packages': packages})

def review_list(request):
    reviews = Review.objects.select_related('customer')
    return render(request, 'admin/review_list.html', {'reviews': reviews})

def vehicle_list(request):
    vehicles = Vehicle.objects.select_related('package')
    return render(request, 'admin/vehicle_list.html', {'vehicles': vehicles})


def vehicle_list1(request):
    vehicles = Vehicle.objects.select_related('package')
    return render(request, 'admin/vehicle_list1.html', {'vehicles': vehicles})

def delete_package(request, id):
    package = get_object_or_404(Package, id=id)
    package.delete()
    return redirect('admin')  # change 'packages' to your package list view name



@login_required
def checkout(request, package_id, vehicle_id):
    package = get_object_or_404(Package, id=package_id)
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    customer = get_object_or_404(Customer, user=request.user)

    if request.method == 'POST':
        people = int(request.POST.get('people_count'))
        total_price = float(request.POST.get('total_price'))

        booking = Booking.objects.create(
            customer=customer,
            travel_package=package,
            number_of_people=people,
            total_price=total_price,
            status='Confirmed'
        )

        return redirect('payment_success', booking_id=booking.id)

    return render(request, 'checkout.html', {'package': package, 'vehicle': vehicle})

def confirm_booking(request):
    if request.method == 'POST':
        package_id = request.POST.get('package_id')
        vehicle_id = request.POST.get('vehicle_id')
        total_price = request.POST.get('total_price')
        people_count = request.POST.get('people_count')

        package = get_object_or_404(Package, id=package_id)
        vehicle = get_object_or_404(Vehicle, id=vehicle_id)
        customer = get_object_or_404(Customer, user=request.user)

        booking = Booking.objects.create(
            customer=customer,
            travel_package=package,
            number_of_people=people_count,
            vehicle=vehicle,
            total_price=total_price,
            status='Pending'
        )
        return redirect('payment_success')  # create this template/view
    return redirect('home')



@login_required
def create_booking(request, package_id):
    package = get_object_or_404(Package, id=package_id)
    customer = get_object_or_404(Customer, user=request.user)

    if request.method == 'POST':
        persons = int(request.POST.get('number_of_people'))

        # Example price logic (you can adjust this)
        base_price_per_person = 1000  # or use dynamic pricing if needed
        total_price = base_price_per_person * persons

        # Create Razorpay order
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        payment = client.order.create({
            'amount': int(total_price * 100),  # amount in paise
            'currency': 'INR',
            'payment_capture': 1
        })

        # Save booking (not paid yet)
        booking = Booking.objects.create(
            customer=customer,
            travel_package=package,
            number_of_people=persons,
            total_price=total_price,
            status='Pending'
        )

        return render(request, 'payment.html', {
            'booking': booking,
            'order_id': payment['id'],
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'amount': total_price * 100,  # for Razorpay JS
        })

    return render(request, 'booking_form.html', {'package': package})

@csrf_exempt
def payment_success(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    booking.is_paid = True
    booking.status = 'Confirmed'
    booking.payment_id = request.POST.get('razorpay_payment_id')
    booking.save()
    return render(request, 'booking_confirmation.html', {'booking': booking})

@login_required
def view_bookings(request):
    customer = Customer.objects.get(user=request.user)
    bookings = Booking.objects.filter(customer=customer).order_by('-booking_date')
    return render(request, 'view_bookings.html', {'bookings': bookings})
