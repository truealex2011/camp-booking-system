"""Booking service logic."""
import random
import string
from datetime import date, datetime, timedelta
from sqlalchemy import and_, func
from app.models import db, Booking, Service
from app.utils.validators import PhoneValidator, DateValidator, TimeSlotValidator, NameValidator, CampValidator


class BookingService:
    """Service for handling booking operations."""
    
    @staticmethod
    def generate_reference_number():
        """Generate a unique booking reference number.
        
        Format: YYYYMMDD-XXXX (date + 4 random alphanumeric)
        
        Returns:
            Unique reference number string
        """
        date_part = date.today().strftime('%Y%m%d')
        
        # Generate random alphanumeric suffix
        while True:
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            reference = f'{date_part}-{random_part}'
            
            # Check if this reference already exists
            existing = Booking.query.filter_by(reference_number=reference).first()
            if not existing:
                return reference
    
    @staticmethod
    def is_slot_available(booking_date, time_slot, max_bookings=2):
        """Check if a time slot is available.
        
        Args:
            booking_date: Date object
            time_slot: Time slot string (HH:MM)
            max_bookings: Maximum bookings per slot
            
        Returns:
            True if available, False otherwise
        """
        count = Booking.query.filter(
            and_(
                Booking.date == booking_date,
                Booking.time_slot == time_slot,
                Booking.status == 'confirmed'
            )
        ).count()
        
        return count < max_bookings
    
    @staticmethod
    def get_slot_count(booking_date, time_slot):
        """Get the number of confirmed bookings for a slot.
        
        Args:
            booking_date: Date object
            time_slot: Time slot string (HH:MM)
            
        Returns:
            Number of confirmed bookings
        """
        return Booking.query.filter(
            and_(
                Booking.date == booking_date,
                Booking.time_slot == time_slot,
                Booking.status == 'confirmed'
            )
        ).count()
    
    @staticmethod
    def get_available_slots(booking_date, time_slots, max_bookings=2):
        """Get available time slots for a date.
        
        Args:
            booking_date: Date object
            time_slots: List of time slot strings
            max_bookings: Maximum bookings per slot
            
        Returns:
            List of available time slot strings
        """
        available = []
        
        for slot in time_slots:
            if BookingService.is_slot_available(booking_date, slot, max_bookings):
                available.append(slot)
        
        return available
    
    @staticmethod
    def validate_booking_data(service_id, booking_date, time_slot, last_name, first_name, phone, camp, valid_camps):
        """Validate booking data.
        
        Args:
            service_id: Service ID
            booking_date: Date object or string
            time_slot: Time slot string
            last_name: Last name
            first_name: First name
            phone: Phone number
            camp: Camp name
            valid_camps: List of valid camp names
            
        Returns:
            Tuple of (is_valid, error_dict)
        """
        errors = {}
        
        # Validate service exists
        service = Service.query.get(service_id)
        if not service:
            errors['service'] = 'Услуга не найдена'
        elif not service.active:
            errors['service'] = 'Услуга недоступна'
        
        # Validate date
        if isinstance(booking_date, str):
            try:
                booking_date = datetime.strptime(booking_date, '%Y-%m-%d').date()
            except ValueError:
                errors['date'] = 'Неверный формат даты'
        
        if not DateValidator.validate_date(booking_date):
            errors['date'] = 'Дата не может быть в прошлом'
        elif not DateValidator.validate_date_range(booking_date):
            errors['date'] = 'Дата выходит за допустимый диапазон'
        
        # Validate time slot
        if not TimeSlotValidator.validate_time_slot(time_slot):
            errors['time_slot'] = 'Неверный формат времени'
        
        # Validate names
        if not NameValidator.validate_name(last_name):
            errors['last_name'] = 'Фамилия должна содержать только кириллицу (2-50 символов)'
        
        if not NameValidator.validate_name(first_name):
            errors['first_name'] = 'Имя должно содержать только кириллицу (2-50 символов)'
        
        # Validate phone
        if not PhoneValidator.validate_phone(phone):
            errors['phone'] = 'Неверный формат телефона. Используйте формат +7 (XXX) XXX-XX-XX'
        
        # Validate camp
        if not CampValidator.validate_camp(camp, valid_camps):
            errors['camp'] = 'Неверный выбор лагеря'
        
        return len(errors) == 0, errors
    
    @staticmethod
    def create_booking(service_id, booking_date, time_slot, last_name, first_name, phone, camp, valid_camps, max_bookings=2):
        """Create a new booking.
        
        Args:
            service_id: Service ID
            booking_date: Date object
            time_slot: Time slot string
            last_name: Last name
            first_name: First name
            phone: Phone number
            camp: Camp name
            valid_camps: List of valid camp names
            max_bookings: Maximum bookings per slot
            
        Returns:
            Tuple of (booking_object or None, error_dict)
        """
        # Validate data
        is_valid, errors = BookingService.validate_booking_data(
            service_id, booking_date, time_slot, last_name, first_name, phone, camp, valid_camps
        )
        
        if not is_valid:
            return None, errors
        
        # Check slot availability (with transaction safety)
        if not BookingService.is_slot_available(booking_date, time_slot, max_bookings):
            return None, {'time_slot': 'К сожалению, это время уже занято. Пожалуйста, выберите другое время.'}
        
        # Format phone number
        formatted_phone = PhoneValidator.format_phone(phone)
        if not formatted_phone:
            return None, {'phone': 'Не удалось отформатировать номер телефона'}
        
        # Generate reference number
        reference_number = BookingService.generate_reference_number()
        
        # Create booking
        booking = Booking(
            service_id=service_id,
            date=booking_date,
            time_slot=time_slot,
            last_name=last_name.strip(),
            first_name=first_name.strip(),
            phone=formatted_phone,
            camp=camp,
            status='confirmed',
            reference_number=reference_number
        )
        
        db.session.add(booking)
        db.session.commit()
        
        return booking, {}
    
    @staticmethod
    def get_booking_by_id(booking_id):
        """Get a booking by ID.
        
        Args:
            booking_id: Booking ID
            
        Returns:
            Booking object or None
        """
        return Booking.query.get(booking_id)
    
    @staticmethod
    def get_booking_by_reference(reference_number):
        """Get a booking by reference number.
        
        Args:
            reference_number: Reference number
            
        Returns:
            Booking object or None
        """
        return Booking.query.filter_by(reference_number=reference_number).first()
    
    @staticmethod
    def get_todays_bookings():
        """Get all confirmed bookings for today.
        
        Returns:
            List of Booking objects sorted by time slot
        """
        today = date.today()
        return Booking.query.filter(
            and_(
                Booking.date == today,
                Booking.status == 'confirmed'
            )
        ).order_by(Booking.time_slot).all()
    
    @staticmethod
    def get_bookings_by_date(booking_date):
        """Get all bookings for a specific date.
        
        Args:
            booking_date: Date object
            
        Returns:
            List of Booking objects
        """
        return Booking.query.filter_by(date=booking_date).order_by(Booking.time_slot).all()
    
    @staticmethod
    def get_bookings_by_filter(service_id=None, booking_date=None, camp=None, status=None):
        """Get bookings by filter criteria.
        
        Args:
            service_id: Service ID (optional)
            booking_date: Date object (optional)
            camp: Camp name (optional)
            status: Status string (optional)
            
        Returns:
            List of Booking objects
        """
        query = Booking.query
        
        if service_id:
            query = query.filter_by(service_id=service_id)
        
        if booking_date:
            query = query.filter_by(date=booking_date)
        
        if camp:
            query = query.filter_by(camp=camp)
        
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(Booking.date.desc(), Booking.time_slot).all()
    
    @staticmethod
    def cancel_booking(booking_id):
        """Cancel a booking.
        
        Args:
            booking_id: Booking ID
            
        Returns:
            True if successful, False otherwise
        """
        booking = Booking.query.get(booking_id)
        if not booking:
            return False
        
        booking.status = 'cancelled'
        db.session.commit()
        return True
    
    @staticmethod
    def update_booking(booking_id, booking_date=None, time_slot=None, last_name=None, first_name=None, phone=None, camp=None, valid_camps=None, max_bookings=2):
        """Update a booking.
        
        Args:
            booking_id: Booking ID
            booking_date: New date (optional)
            time_slot: New time slot (optional)
            last_name: New last name (optional)
            first_name: New first name (optional)
            phone: New phone (optional)
            camp: New camp (optional)
            valid_camps: List of valid camp names
            max_bookings: Maximum bookings per slot
            
        Returns:
            Tuple of (success, error_dict)
        """
        booking = Booking.query.get(booking_id)
        if not booking:
            return False, {'booking': 'Бронирование не найдено'}
        
        errors = {}
        
        # If changing date or time slot, check availability
        new_date = booking_date if booking_date else booking.date
        new_slot = time_slot if time_slot else booking.time_slot
        
        if (booking_date or time_slot) and (new_date != booking.date or new_slot != booking.time_slot):
            # Check if new slot is available
            count = Booking.query.filter(
                and_(
                    Booking.date == new_date,
                    Booking.time_slot == new_slot,
                    Booking.status == 'confirmed',
                    Booking.id != booking_id  # Exclude current booking
                )
            ).count()
            
            if count >= max_bookings:
                errors['time_slot'] = 'Выбранное время уже занято'
                return False, errors
        
        # Update fields
        if booking_date:
            if not DateValidator.validate_date(booking_date):
                errors['date'] = 'Дата не может быть в прошлом'
            else:
                booking.date = booking_date
        
        if time_slot:
            if not TimeSlotValidator.validate_time_slot(time_slot):
                errors['time_slot'] = 'Неверный формат времени'
            else:
                booking.time_slot = time_slot
        
        if last_name:
            if not NameValidator.validate_name(last_name):
                errors['last_name'] = 'Фамилия должна содержать только кириллицу'
            else:
                booking.last_name = last_name.strip()
        
        if first_name:
            if not NameValidator.validate_name(first_name):
                errors['first_name'] = 'Имя должно содержать только кириллицу'
            else:
                booking.first_name = first_name.strip()
        
        if phone:
            formatted_phone = PhoneValidator.format_phone(phone)
            if not formatted_phone:
                errors['phone'] = 'Неверный формат телефона'
            else:
                booking.phone = formatted_phone
        
        if camp and valid_camps:
            if not CampValidator.validate_camp(camp, valid_camps):
                errors['camp'] = 'Неверный выбор лагеря'
            else:
                booking.camp = camp
        
        if errors:
            return False, errors
        
        db.session.commit()
        return True, {}
    
    @staticmethod
    def get_statistics(start_date=None, end_date=None):
        """Get booking statistics.
        
        Args:
            start_date: Start date (optional)
            end_date: End date (optional)
            
        Returns:
            Dictionary with statistics
        """
        query = Booking.query.filter_by(status='confirmed')
        
        if start_date:
            query = query.filter(Booking.date >= start_date)
        
        if end_date:
            query = query.filter(Booking.date <= end_date)
        
        bookings = query.all()
        
        # Count by service
        by_service = {}
        for booking in bookings:
            service_name = booking.service.name if booking.service else 'Unknown'
            by_service[service_name] = by_service.get(service_name, 0) + 1
        
        # Count by camp
        by_camp = {}
        for booking in bookings:
            by_camp[booking.camp] = by_camp.get(booking.camp, 0) + 1
        
        return {
            'total': len(bookings),
            'by_service': by_service,
            'by_camp': by_camp
        }
