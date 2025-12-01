import re
from datetime import date, timedelta
from django.core.exceptions import ValidationError


def validate_phone_number(value):
    """
    Validates phone number format: must match regex ^07\\d{8}$
    Example: 0712345678
    """
    pattern = r'^07\d{8}$'
    if not re.match(pattern, value):
        raise ValidationError(
            'Contact number must start with 07 and be exactly 10 digits long (e.g., 0712345678).'
        )


def validate_booking_date(value):
    """
    Validates that the booking date is within the next 30 days.
    Date cannot be in the past or more than 30 days in the future.
    """
    today = date.today()
    max_date = today + timedelta(days=30)
    
    if value < today:
        raise ValidationError(
            'Booking date cannot be in the past. Please select today or a future date.'
        )
    
    if value > max_date:
        raise ValidationError(
            f'Booking date cannot be more than 30 days in the future. '
            f'Please select a date before {max_date.strftime("%B %d, %Y")}.'
        )

