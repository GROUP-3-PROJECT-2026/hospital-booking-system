# hospital-booking-system


Scenario:

A hospital intends to replace its manual booking system with a simple online application. 
Patients should be able to book medical tests such as X-ray, Ultrasound, or Blood Test. The hospital management requires the system to:
  1. Collect accurate booking details.
  2. Prevent double bookings for the same patient, test, date, and time.
  3. Display all bookings for administrative review.
  4. Ensure the system is user-friendly, reliable, and scalable.

User Interface & Usability
  1.Develop a booking form with the following fields:
  Patient Name, 
  Age, Contact Number,
  Test Type, 
  Date, Time, 
  Hospital Name
  
Ensure a clean, professional interface suitable for business use.
Include accessibility features and user guidance messages.


Bookings Management
  Display submitted bookings in a structured table or list.
  Include details such as Patient Name, Test Type, Date, and Hospital Name.
  New bookings should appear instantly.
  Allow filtering or searching by patient name or test type for easier management.
  Patients Table → Stores patient info


Tests Table → Stores available tests


Bookings Table → Stores all bookings and links patients to table




Phase 1: Setup Repository
  -   Initialize Django project, create virtual environment, and install django.

Phase 2: Database Architecture
  -  Authentication: Set up User Registration (Patient Registration) to store credentials. (Database)

Phase 3: Front-end Interface
  -  User sign up/sign in page
  -  Admin Dashboard
  -  Booking interface

Phase 4: Backend Logic & Validation

Phase 5 : Testing and Deployment

