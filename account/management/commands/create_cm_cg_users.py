from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from account.models import User
from datetime import date


class Command(BaseCommand):
    help = 'Create test case managers and caregivers'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("Creating Case Managers and Caregivers Test Data")
        self.stdout.write("=" * 60)
        
        # Check existing users
        self.stdout.write("\n📊 Current Status:")
        self.stdout.write(f"Case Managers: {User.objects.filter(role='case_manager').count()}")
        self.stdout.write(f"Caregivers: {User.objects.filter(role='caregiver').count()}")
        
        # Create Case Managers
        case_managers_data = [
            {
                'username': 'casemanager1',
                'email': 'casemanager1@beihoo.com',
                'first_name': '美玲',
                'last_name': '王',
                'phone_number': '0912-345-001',
                'date_of_birth': date(1985, 5, 15),
            },
            {
                'username': 'casemanager2',
                'email': 'casemanager2@beihoo.com',
                'first_name': '淑芬',
                'last_name': '李',
                'phone_number': '0912-345-002',
                'date_of_birth': date(1988, 8, 22),
            },
            {
                'username': 'casemanager3',
                'email': 'casemanager3@beihoo.com',
                'first_name': '雅惠',
                'last_name': '陳',
                'phone_number': '0912-345-003',
                'date_of_birth': date(1990, 3, 10),
            },
        ]
        
        self.stdout.write("\n👥 Creating Case Managers...")
        created_cm = 0
        for data in case_managers_data:
            if not User.objects.filter(username=data['username']).exists():
                user = User.objects.create(
                    username=data['username'],
                    email=data['email'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    phone_number=data['phone_number'],
                    date_of_birth=data['date_of_birth'],
                    role='case_manager',
                    is_active=True,
                    password=make_password('test1234')
                )
                self.stdout.write(self.style.SUCCESS(f"✓ Created: {data['username']} - {data['last_name']}{data['first_name']}"))
                created_cm += 1
            else:
                self.stdout.write(self.style.WARNING(f"⊗ Skipped: {data['username']} (already exists)"))
        
        # Create Caregivers
        caregivers_data = [
            {
                'username': 'caregiver1',
                'email': 'caregiver1@beihoo.com',
                'first_name': '小華',
                'last_name': '張',
                'phone_number': '0912-345-011',
                'date_of_birth': date(1987, 6, 18),
            },
            {
                'username': 'caregiver2',
                'email': 'caregiver2@beihoo.com',
                'first_name': '美珍',
                'last_name': '林',
                'phone_number': '0912-345-012',
                'date_of_birth': date(1989, 11, 25),
            },
            {
                'username': 'caregiver3',
                'email': 'caregiver3@beihoo.com',
                'first_name': '秀英',
                'last_name': '黃',
                'phone_number': '0912-345-013',
                'date_of_birth': date(1992, 4, 8),
            },
            {
                'username': 'caregiver4',
                'email': 'caregiver4@beihoo.com',
                'first_name': '佳玲',
                'last_name': '劉',
                'phone_number': '0912-345-014',
                'date_of_birth': date(1986, 9, 30),
            },
        ]
        
        self.stdout.write("\n👥 Creating Caregivers...")
        created_cg = 0
        for data in caregivers_data:
            if not User.objects.filter(username=data['username']).exists():
                user = User.objects.create(
                    username=data['username'],
                    email=data['email'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    phone_number=data['phone_number'],
                    date_of_birth=data['date_of_birth'],
                    role='caregiver',
                    is_active=True,
                    password=make_password('test1234')
                )
                self.stdout.write(self.style.SUCCESS(f"✓ Created: {data['username']} - {data['last_name']}{data['first_name']}"))
                created_cg += 1
            else:
                self.stdout.write(self.style.WARNING(f"⊗ Skipped: {data['username']} (already exists)"))
        
        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("📋 Summary:")
        self.stdout.write(f"Case Managers created: {created_cm}")
        self.stdout.write(f"Caregivers created: {created_cg}")
        self.stdout.write(f"\nTotal Case Managers: {User.objects.filter(role='case_manager').count()}")
        self.stdout.write(f"Total Caregivers: {User.objects.filter(role='caregiver').count()}")
        self.stdout.write("\n🔐 Login Credentials:")
        self.stdout.write("   Username: casemanager1, casemanager2, casemanager3")
        self.stdout.write("   Username: caregiver1, caregiver2, caregiver3, caregiver4")
        self.stdout.write("   Password: test1234 (for all users)")
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("✅ Case Manager and Caregiver test data creation complete!"))
