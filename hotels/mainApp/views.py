from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Room, Reservation, Booking, Notification
from .forms import ReservationForm
from django.contrib.auth.models import User

# Перенаправление на страницу hotels-main в случае попадения на страницу с отсутствующим доменом
def redirect_to_main(request):
    return redirect("hotels-main")

# Регистрация с последующим перенаправлением на логин
def register(request):
    from django.contrib import messages
    from mainApp.forms import UserRegisterForm
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, "Вы успешно зарегистрировались")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'registration.html', {"reg_form": form})

def main_page_view(request):
    # Получаем все комнаты
    rooms = Room.objects.all()

    # Получаем последние бронирования
    bookings = Booking.objects.order_by('-booking_date')[:5]

    context = {
        'rooms': rooms,
        'bookings': bookings,
    }

    return render(request, 'mainPage.html', context)

# цена = цена отеля за день * на (дата выезда - дата въезда) * на кол-во гостей
def calculate_total_price(room, check_in_date, check_out_date, guest_count):
    total_price = room.price * (check_out_date - check_in_date).days * guest_count
    return total_price


def reserve_hotel_view(request):
    message = ""
    context = {}
    if request.method == 'POST':
        search_query = request.POST.get('search_query')
        form = ReservationForm(request.POST)
        if form.is_valid():
            check_in_date = form.cleaned_data['check_in_date']
            check_out_date = form.cleaned_data['check_out_date']
            guest_count = form.cleaned_data['guest_count']

            if search_query:
                hotels = Room.objects.filter(hotel_name__icontains=search_query)
                if hotels.exists():
                    room = hotels.first()
                    total_price = calculate_total_price(room, check_in_date, check_out_date, guest_count)
                    context = {'form': form, 'hotels': hotels, 'search_query': search_query, 'totalprice': total_price,"check_in_date":check_in_date,"check_out_date":check_out_date,"guest_count":guest_count}
                else:
                    message = "Не удалось найти отель с таким именем."
                    context = {'form': form, 'message': message}
            else:
                message = "Выберите отель для продолжения."
                context = {'form': form, 'message': message}
        else:
            message = "Форма заполнена неверно. Пожалуйста, исправьте ошибки."
            context = {'form': form, 'message': message}
    else:
        form = ReservationForm()
        context = {'form': form, 'message': message}



    return render(request, 'reserveHotel.html', context)

# def reserve_hotel_view(request):
#     if request.method == 'POST':
#         form = ReservationForm(request.POST)
#         if form.is_valid():
#             check_in_date = form.cleaned_data['check_in_date']
#             check_out_date = form.cleaned_data['check_out_date']
#             guest_count = form.cleaned_data['guest_count']
#             room_id = request.POST.get('room_id')  # Получаем id выбранного номера
#             room = Room.objects.get(id=room_id)
#
#
#             # Сохранение данных о бронировании
#             reservation = Reservation.objects.create(
#                 room=room,
#                 check_in_date=check_in_date,
#                 check_out_date=check_out_date,
#                 guest_count=guest_count
#             )
#             # Перенаправление на страницу оплаты
#             return redirect('payment-page')
#     else:
#         form = ReservationForm()
#
#     context = {'form': form}
#     return render(request, 'reserveHotel.html', context)


def profile_view(request):
    print("start_profile")
    if request.user.is_authenticated:
        user_id = request.user.id
        print(user_id)
        user = User.objects.get(id=user_id)
        reservations = Reservation.objects.filter(user_id=user_id)

        context = {
            'full_name': user.username,  # Заменим на нужный атрибут пользователя
            'reservations': reservations,
        }
        return render(request, 'profilePage.html', context)
    else:
        return redirect('login')

def payment_view(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            user_id = request.user.id
        else:
            return redirect("login")
        print(request.POST.get("room_id"))
        form = ReservationForm(request.POST)

        if form.is_valid() or True:
            print("valid")
            check_in_date = request.POST.get('check_in_date') #TODO: конвертировать в формат YYYY-MM-DD
            check_out_date = request.POST.get('check_out_date') #TODO: конвертировать в формат YYYY-MM-DD
            guest_count = request.POST.get('guest_count')
            room_id = request.POST.get('room_id')  # Получаем id выбранного номера
            room = Room.objects.get(id=room_id)
            user = User.objects.get(id=user_id)
            # Сохранение данных о бронировании
            reservation = Reservation.objects.create(
                room=room,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                guest_count=guest_count,
                user_id=user
            )
            reservation.save()
            # Перенаправление на страницу оплаты
            return redirect('payment-page')
    else:
        form = ReservationForm()

    context = {'form': form}
    return render(request, 'paymentPage.html', context)