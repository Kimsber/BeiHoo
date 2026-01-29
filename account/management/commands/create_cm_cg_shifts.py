from django.core.management.base import BaseCommand
from account.models import User
from dashboard.models import Shift
from datetime import date, time, timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = 'Create test shifts for case managers and caregivers'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("Creating Shifts for Case Managers and Caregivers")
        self.stdout.write("=" * 60)
        
        # Get case managers and caregivers
        case_managers = User.objects.filter(role='case_manager', is_active=True)
        caregivers = User.objects.filter(role='caregiver', is_active=True)
        
        self.stdout.write(f"\n📊 Found {case_managers.count()} case managers")
        self.stdout.write(f"📊 Found {caregivers.count()} caregivers")
        
        today = timezone.now().date()
        created_count = 0
        
        # Create shifts for next 14 days
        self.stdout.write("\n🗓️  Creating shifts for the next 14 days...")
        
        # Case Managers - typically work morning or afternoon shifts
        shift_patterns_cm = [
            {'shift_type': 'morning', 'start': time(8, 0), 'end': time(12, 0), 'location': '個管室'},
            {'shift_type': 'afternoon', 'start': time(13, 0), 'end': time(17, 0), 'location': '個管室'},
            {'shift_type': 'morning', 'start': time(8, 30), 'end': time(16, 30), 'location': '個管室'},
        ]
        
        for i, cm in enumerate(case_managers):
            pattern = shift_patterns_cm[i % len(shift_patterns_cm)]
            self.stdout.write(f"\n👤 Creating shifts for {cm.get_full_name()}...")
            
            for day_offset in range(14):
                shift_date = today + timedelta(days=day_offset)
                
                # Skip weekends for case managers
                if shift_date.weekday() >= 5:
                    continue
                
                # Check if shift already exists
                if Shift.objects.filter(user=cm, date=shift_date).exists():
                    continue
                
                shift = Shift.objects.create(
                    user=cm,
                    shift_type=pattern['shift_type'],
                    date=shift_date,
                    start_time=pattern['start'],
                    end_time=pattern['end'],
                    location=pattern['location'],
                    status='confirmed',
                    notes='個案管理業務'
                )
                created_count += 1
                if day_offset < 3:  # Only print first 3 days
                    self.stdout.write(f"  ✓ {shift_date.strftime('%m/%d')} ({shift.get_shift_type_display()}) {shift.start_time.strftime('%H:%M')}-{shift.end_time.strftime('%H:%M')}")
        
        # Caregivers - work various shifts including evenings
        shift_patterns_cg = [
            {'shift_type': 'morning', 'start': time(7, 0), 'end': time(15, 0), 'location': '照護區'},
            {'shift_type': 'afternoon', 'start': time(15, 0), 'end': time(23, 0), 'location': '照護區'},
            {'shift_type': 'evening', 'start': time(14, 0), 'end': time(22, 0), 'location': '照護區'},
            {'shift_type': 'night', 'start': time(23, 0), 'end': time(7, 0), 'location': '照護區'},
        ]
        
        for i, cg in enumerate(caregivers):
            pattern = shift_patterns_cg[i % len(shift_patterns_cg)]
            self.stdout.write(f"\n👤 Creating shifts for {cg.get_full_name()}...")
            
            for day_offset in range(14):
                shift_date = today + timedelta(days=day_offset)
                
                # Caregivers work 7 days a week in rotation
                # Skip some days based on pattern
                if i % 2 == 0 and shift_date.weekday() in [2, 5]:  # Skip Wed, Sat for some
                    continue
                
                # Check if shift already exists
                if Shift.objects.filter(user=cg, date=shift_date).exists():
                    continue
                
                shift = Shift.objects.create(
                    user=cg,
                    shift_type=pattern['shift_type'],
                    date=shift_date,
                    start_time=pattern['start'],
                    end_time=pattern['end'],
                    location=pattern['location'],
                    status='confirmed',
                    notes='病患照護服務'
                )
                created_count += 1
                if day_offset < 3:  # Only print first 3 days
                    self.stdout.write(f"  ✓ {shift_date.strftime('%m/%d')} ({shift.get_shift_type_display()}) {shift.start_time.strftime('%H:%M')}-{shift.end_time.strftime('%H:%M')}")
        
        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("📋 Summary:")
        self.stdout.write(f"Total shifts created: {created_count}")
        self.stdout.write(f"\nCase Manager shifts: {Shift.objects.filter(user__role='case_manager').count()}")
        self.stdout.write(f"Caregiver shifts: {Shift.objects.filter(user__role='caregiver').count()}")
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("✅ Shift creation complete!"))
