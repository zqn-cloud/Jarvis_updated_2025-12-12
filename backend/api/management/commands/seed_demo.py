from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date
from api.models import User, CalendarType, Event, EventLink


class Command(BaseCommand):
    help = 'Seed demo data for jarvis@cuhk.com account'

    def handle(self, *args, **options):
        # Get or create demo user
        user, created = User.objects.get_or_create(
            account_id='jarvis@cuhk.com',
            defaults={
                'home_address': '123 Main Street, Sha Tin',
                'school_address': 'CUHK, Sha Tin, Hong Kong'
            }
        )
        
        if not created:
            user.home_address = '123 Main Street, Sha Tin'
            user.school_address = 'CUHK, Sha Tin, Hong Kong'
            user.save()
        
        self.stdout.write(f'User: {user.account_id}')
        
        # Delete existing calendar types and events for this user
        CalendarType.objects.filter(user=user).delete()
        Event.objects.filter(user=user).delete()
        
        # Create calendar types
        types_data = [
            {'type_id': 'general', 'name': 'General', 'color': '#6B7280', 'is_deletable': False},
            {'type_id': 'routine', 'name': 'Routine', 'color': '#EC4899', 'is_deletable': True},
            {'type_id': 'events', 'name': 'Events', 'color': '#F59E0B', 'is_deletable': True},
            {'type_id': 'holidays', 'name': 'Holidays', 'color': '#3B82F6', 'is_deletable': True},
            {'type_id': 'school', 'name': 'School', 'color': '#22C55E', 'is_deletable': True},
        ]
        
        calendar_types = {}
        for type_data in types_data:
            ct = CalendarType.objects.create(user=user, **type_data)
            calendar_types[type_data['type_id']] = ct
            self.stdout.write(f'Created type: {type_data["name"]}')
        
        # Calculate dates
        today = date.today()
        yesterday = today - timedelta(days=1)
        two_days_ago = today - timedelta(days=2)
        tomorrow = today + timedelta(days=1)
        two_days_later = today + timedelta(days=2)
        three_days_later = today + timedelta(days=3)
        
        # Create events
        events_data = [
            # Two days ago
            {
                'title': 'Gym Session',
                'date': two_days_ago,
                'is_all_day': False,
                'start_time': '07:00',
                'end_time': '08:30',
                'calendar_type': calendar_types['routine'],
                'completed': False
            },
            {
                'title': 'Black Friday Shopping',
                'date': two_days_ago,
                'is_all_day': True,
                'calendar_type': calendar_types['events'],
                'completed': True
            },
            # Yesterday
            {
                'title': 'Weekend Brunch',
                'date': yesterday,
                'is_all_day': False,
                'start_time': '10:00',
                'end_time': '12:00',
                'calendar_type': calendar_types['events'],
                'completed': False
            },
            {
                'title': 'Study for Exams',
                'date': yesterday,
                'is_all_day': False,
                'start_time': '14:00',
                'end_time': '18:00',
                'calendar_type': calendar_types['school'],
                'completed': False
            },
            # Today
            {
                'title': 'KAI BIRTHDAY TOMORROW',
                'date': today,
                'is_all_day': True,
                'calendar_type': calendar_types['events'],
                'completed': False
            },
            {
                'title': 'SIGN UP TO UNI',
                'date': today,
                'is_all_day': True,
                'calendar_type': calendar_types['events'],
                'completed': True,
                'links': ['https://university.edu/apply']
            },
            {
                'title': 'Therapy',
                'date': today,
                'is_all_day': False,
                'start_time': '15:00',
                'end_time': '17:00',
                'calendar_type': calendar_types['routine'],
                'completed': False
            },
            {
                'title': 'Morning Yoga',
                'date': today,
                'is_all_day': False,
                'start_time': '06:30',
                'end_time': '07:30',
                'calendar_type': calendar_types['routine'],
                'completed': True
            },
            # Tomorrow
            {
                'title': "Kai's Birthday Party",
                'date': tomorrow,
                'is_all_day': False,
                'start_time': '18:00',
                'end_time': '22:00',
                'location': "Kai's House",
                'calendar_type': calendar_types['events'],
                'completed': False
            },
            {
                'title': 'Start of Advent',
                'date': tomorrow,
                'is_all_day': True,
                'calendar_type': calendar_types['holidays'],
                'completed': False
            },
            # Two days later
            {
                'title': 'Project Deadline',
                'date': two_days_later,
                'is_all_day': True,
                'calendar_type': calendar_types['school'],
                'completed': False
            },
            {
                'title': 'Team Meeting',
                'date': two_days_later,
                'is_all_day': False,
                'start_time': '10:00',
                'end_time': '11:00',
                'calendar_type': calendar_types['general'],
                'completed': False
            },
            # Three days later
            {
                'title': 'Doctor Appointment',
                'date': three_days_later,
                'is_all_day': False,
                'start_time': '09:00',
                'end_time': '10:00',
                'location': 'City Hospital',
                'calendar_type': calendar_types['routine'],
                'completed': False
            },
        ]
        
        for event_data in events_data:
            links = event_data.pop('links', [])
            event = Event.objects.create(user=user, **event_data)
            
            for url in links:
                EventLink.objects.create(event=event, url=url)
            
            self.stdout.write(f'Created event: {event.title}')
        
        self.stdout.write(self.style.SUCCESS(f'\nDemo data seeded successfully for {user.account_id}!'))
        self.stdout.write(f'Total events: {Event.objects.filter(user=user).count()}')

