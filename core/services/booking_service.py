from core.models import Booking


def check_duplicate_booking(patient, test, date, time):
    """
    Checks if a booking already exists for the given patient, test, date, and time.
    
    Args:
        patient: Patient instance
        test: Test instance
        date: Date object
        time: Time object
    
    Returns:
        bool: True if duplicate booking exists, False otherwise
    """
    return Booking.objects.filter(
        patient=patient,
        test=test,
        date=date,
        time=time
    ).exists()

