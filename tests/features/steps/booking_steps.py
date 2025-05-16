from behave import given, when, then
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from event_booking.domain.entities.event import Event
from event_booking.domain.entities.session import Session
from event_booking.domain.entities.booking import BookingStatus
from event_booking.domain.services.event_service import EventService
from event_booking.domain.services.booking_service import BookingService
from event_booking.infrastructure.persistence.mariadb_event_repository import MariaDBEventRepository
from event_booking.infrastructure.persistence.mariadb_booking_repository import MariaDBBookingRepository
from event_booking.infrastructure.persistence.connection_pool import DatabaseConnectionPool

@given('there is an event "{name}" at "{venue}"')
def step_impl(context, name, venue):
    pool = DatabaseConnectionPool.get_instance()
    event_repository = MariaDBEventRepository(pool)
    context.event_service = EventService(event_repository)
    
    context.event = context.event_service.create_event(
        name=name,
        description=f"Test event: {name}",
        venue=venue,
        categories=["test"]
    )

@given('the event has a session on "{datetime_str}" with {capacity:d} seats at ${price:.2f}')
def step_impl(context, datetime_str, capacity, price):
    start_time = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
    end_time = start_time.replace(hour=start_time.hour + 2)
    
    context.session = context.event_service.add_session(
        event_id=context.event.id,
        start_time=start_time,
        end_time=end_time,
        capacity=capacity,
        base_price=Decimal(str(price))
    )

@given('I am a registered user')
def step_impl(context):
    context.user_id = uuid4()
    pool = DatabaseConnectionPool.get_instance()
    booking_repository = MariaDBBookingRepository(pool)
    event_repository = MariaDBEventRepository(pool)
    context.booking_service = BookingService(booking_repository, event_repository)

@given('{seats:d} seats are already booked for the session')
def step_impl(context, seats):
    # Create a different user to book the seats
    other_user_id = uuid4()
    booking = context.booking_service.create_booking(
        user_id=other_user_id,
        session_id=context.session.id,
        num_seats=seats
    )
    context.booking_service.confirm_booking(booking.id)

@when('I try to book {num_seats:d} seats for the session')
def step_impl(context, num_seats):
    try:
        context.booking = context.booking_service.create_booking(
            user_id=context.user_id,
            session_id=context.session.id,
            num_seats=num_seats
        )
        context.error = None
    except Exception as e:
        context.error = e

@then('the booking should be created successfully')
def step_impl(context):
    assert context.error is None
    assert context.booking is not None
    assert context.booking.user_id == context.user_id
    assert context.booking.session_id == context.session.id

@then('the booking status should be "{status}"')
def step_impl(context, status):
    assert context.booking.status == BookingStatus(status)

@then('the session should have {available:d} available seats')
def step_impl(context, available):
    event = context.event_service.event_repository.find_by_id(context.event.id)
    session = event.get_session(context.session.id)
    assert session.available_seats == available

@then('the price per seat should be ${price:.2f}')
def step_impl(context, price):
    assert context.booking.price_per_seat == Decimal(str(price))

@then('I should get an "{error_type}" error')
def step_impl(context, error_type):
    assert context.error is not None
    assert error_type.lower() in str(context.error).lower()

@given('I have a confirmed booking for {num_seats:d} seats')
def step_impl(context, num_seats):
    context.booking = context.booking_service.create_booking(
        user_id=context.user_id,
        session_id=context.session.id,
        num_seats=num_seats
    )
    context.booking_service.confirm_booking(context.booking.id)

@when('I cancel my booking')
def step_impl(context):
    context.booking = context.booking_service.cancel_booking(context.booking.id)

@when('I book seats with the following occupancy rates')
def step_impl(context):
    context.bookings = []
    for row in context.table:
        booking = context.booking_service.create_booking(
            user_id=context.user_id,
            session_id=context.session.id,
            num_seats=int(row['seats'])
        )
        context.bookings.append((booking, Decimal(row['expected_price'].replace('$', ''))))

@then('all bookings should have the correct prices')
def step_impl(context):
    for booking, expected_price in context.bookings:
        assert booking.price_per_seat == expected_price 