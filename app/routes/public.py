"""Public user-facing routes."""
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, flash
from datetime import datetime, timedelta, date
from app.services.service_manager import ServiceManager
from app.services.booking_service import BookingService
from flask import current_app

bp = Blueprint('public', __name__)


@bp.route('/')
def index():
    """Main page - service selection."""
    services = ServiceManager.get_active_services()
    return render_template('public/index.html', services=services)


@bp.route('/calendar/<int:service_id>')
def calendar(service_id):
    """Calendar page - date and time selection."""
    service = ServiceManager.get_service_by_id(service_id)
    
    if not service or not service.active:
        flash('Услуга не найдена или недоступна', 'error')
        return redirect(url_for('public.index'))
    
    # Store service_id in session
    session['selected_service_id'] = service_id
    
    time_slots = current_app.config['TIME_SLOTS']
    camps = current_app.config['CAMPS']
    
    return render_template('public/calendar.html', service=service, time_slots=time_slots, camps=camps)


@bp.route('/api/slots')
def get_slots():
    """API endpoint to get available slots for a date."""
    date_str = request.args.get('date')
    
    if not date_str:
        return jsonify({'error': 'Date parameter required'}), 400
    
    try:
        booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    # Check if date is valid
    if booking_date < date.today():
        return jsonify({'error': 'Date cannot be in the past'}), 400
    
    max_date = date.today() + timedelta(days=current_app.config['CALENDAR_DAYS_AHEAD'])
    if booking_date > max_date:
        return jsonify({'error': 'Date is too far in the future'}), 400
    
    time_slots = current_app.config['TIME_SLOTS']
    max_bookings = current_app.config['MAX_BOOKINGS_PER_SLOT']
    
    # Get availability for each slot
    slots_data = []
    for slot in time_slots:
        count = BookingService.get_slot_count(booking_date, slot)
        slots_data.append({
            'time': slot,
            'available': count < max_bookings,
            'count': count,
            'max': max_bookings
        })
    
    return jsonify({'slots': slots_data})


@bp.route('/booking', methods=['POST'])
def create_booking():
    """Create a new booking."""
    # Get form data
    service_id = session.get('selected_service_id')
    if not service_id:
        return jsonify({'error': True, 'message': 'Услуга не выбрана'}), 400
    
    date_str = request.form.get('date')
    time_slot = request.form.get('time_slot')
    last_name = request.form.get('last_name')
    first_name = request.form.get('first_name')
    phone = request.form.get('phone')
    camp = request.form.get('camp')
    
    # Validate required fields
    if not all([date_str, time_slot, last_name, first_name, phone, camp]):
        return jsonify({
            'error': True,
            'message': 'Все поля обязательны для заполнения',
            'field_errors': {}
        }), 400
    
    # Parse date
    try:
        booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': True, 'message': 'Неверный формат даты'}), 400
    
    # Create booking
    valid_camps = current_app.config['CAMPS']
    max_bookings = current_app.config['MAX_BOOKINGS_PER_SLOT']
    
    booking, errors = BookingService.create_booking(
        service_id=service_id,
        booking_date=booking_date,
        time_slot=time_slot,
        last_name=last_name,
        first_name=first_name,
        phone=phone,
        camp=camp,
        valid_camps=valid_camps,
        max_bookings=max_bookings
    )
    
    if errors:
        return jsonify({
            'error': True,
            'message': 'Ошибка валидации данных',
            'field_errors': errors
        }), 400
    
    # Clear session
    session.pop('selected_service_id', None)
    
    # Return success with reference number
    return jsonify({
        'success': True,
        'reference_number': booking.reference_number,
        'redirect_url': url_for('public.confirmation', reference_number=booking.reference_number)
    })


@bp.route('/confirmation/<reference_number>')
def confirmation(reference_number):
    """Booking confirmation page."""
    booking = BookingService.get_booking_by_reference(reference_number)
    
    if not booking:
        flash('Бронирование не найдено', 'error')
        return redirect(url_for('public.index'))
    
    # Get required documents for the service
    required_documents = ServiceManager.get_required_documents(booking.service_id)
    if not required_documents:
        required_documents = current_app.config['REQUIRED_DOCUMENTS']
    
    return render_template('public/confirmation.html', booking=booking, required_documents=required_documents)
