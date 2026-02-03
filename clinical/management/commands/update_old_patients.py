from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from account.models import User
from clinical.models import (
    PatientRecord, MedicalRecord, VitalSigns, 
    Medication, MedicationAdministration, NursingNote,
    CarePlan, CarePlanGoal, CareRecord, IncidentReport,
    RehabPlan, RehabSession
)
import random


class Command(BaseCommand):
    help = '更新舊有病患資料 (patient1-patient5)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('開始更新舊有病患資料...'))
        
        # 取得所有必要的人員
        case_managers = list(User.objects.filter(role='case_manager'))
        caregivers = list(User.objects.filter(role='caregiver'))
        doctors = list(User.objects.filter(role='doctor'))
        nurses = list(User.objects.filter(role='nurse'))
        
        if not case_managers or not caregivers:
            self.stdout.write(self.style.ERROR('請先執行 create_patient_test_data 建立案管師和照顧者'))
            return
        
        # 定義舊病患的完整資料
        patients_data = {
            'patient1': {
                'first_name': '金龍',
                'last_name': '王',
                'date_of_birth': '1943-03-10',
                'medical_record_number': 'MRN2023001',
                'primary_diagnosis': '腦中風、高血壓、高血脂',
                'allergies': '磺胺類藥物',
                'emergency_contact_name': '王小明 (兒子)',
                'emergency_contact_phone': '0911-111-001',
            },
            'patient2': {
                'first_name': '玉蘭',
                'last_name': '李',
                'date_of_birth': '1946-06-22',
                'medical_record_number': 'MRN2023002',
                'primary_diagnosis': '糖尿病、慢性腎臟病',
                'allergies': '無',
                'emergency_contact_name': '李大華 (女兒)',
                'emergency_contact_phone': '0911-111-002',
            },
            'patient3': {
                'first_name': '德山',
                'last_name': '陳',
                'date_of_birth': '1949-09-15',
                'medical_record_number': 'MRN2023003',
                'primary_diagnosis': '慢性阻塞性肺病、氣喘',
                'allergies': '花生',
                'emergency_contact_name': '陳淑芬 (配偶)',
                'emergency_contact_phone': '0911-111-003',
            },
            'patient4': {
                'first_name': '秋香',
                'last_name': '張',
                'date_of_birth': '1951-11-30',
                'medical_record_number': 'MRN2023004',
                'primary_diagnosis': '退化性關節炎、骨質疏鬆',
                'allergies': '無',
                'emergency_contact_name': '張志強 (兒子)',
                'emergency_contact_phone': '0911-111-004',
            },
            'patient5': {
                'first_name': '福來',
                'last_name': '劉',
                'date_of_birth': '1944-04-18',
                'medical_record_number': 'MRN2023005',
                'primary_diagnosis': '巴金森氏症、憂鬱症',
                'allergies': 'NSAID類止痛藥',
                'emergency_contact_name': '劉美玲 (女兒)',
                'emergency_contact_phone': '0911-111-005',
            },
        }
        
        updated_count = 0
        
        for username, pdata in patients_data.items():
            try:
                # 取得或更新使用者
                user = User.objects.get(username=username)
                user.first_name = pdata['first_name']
                user.last_name = pdata['last_name']
                user.date_of_birth = pdata['date_of_birth']
                user.role = 'patient'
                if not user.email:
                    user.email = f'{username}@patient.com'
                if not user.phone_number:
                    user.phone_number = f'0911-{username[-1]}00-{username[-1]}01'
                user.save()
                
                # 取得或建立病患記錄
                idx = int(username[-1]) - 1
                record, created = PatientRecord.objects.get_or_create(
                    patient=user,
                    defaults={
                        'medical_record_number': pdata['medical_record_number'],
                        'primary_diagnosis': pdata['primary_diagnosis'],
                        'allergies': pdata['allergies'],
                        'emergency_contact_name': pdata['emergency_contact_name'],
                        'emergency_contact_phone': pdata['emergency_contact_phone'],
                        'case_manager': case_managers[idx % len(case_managers)],
                        'caregiver': caregivers[idx % len(caregivers)],
                        'admission_date': timezone.now() - timedelta(days=random.randint(60, 200)),
                        'status': 'active',
                        'notes': f'舊有病患資料更新於 {timezone.now().strftime("%Y-%m-%d")}',
                    }
                )
                
                if not created:
                    # 更新現有記錄
                    record.primary_diagnosis = pdata['primary_diagnosis']
                    record.allergies = pdata['allergies']
                    record.emergency_contact_name = pdata['emergency_contact_name']
                    record.emergency_contact_phone = pdata['emergency_contact_phone']
                    if not record.case_manager:
                        record.case_manager = case_managers[idx % len(case_managers)]
                    if not record.caregiver:
                        record.caregiver = caregivers[idx % len(caregivers)]
                    record.save()
                    self.stdout.write(f'✓ 更新病患: {user.username} ({user.get_full_name()})')
                else:
                    self.stdout.write(f'✓ 建立病患記錄: {user.username} ({user.get_full_name()})')
                
                # 為舊病患建立基本臨床記錄（如果沒有的話）
                # 1. 醫療記錄
                if not MedicalRecord.objects.filter(patient=user).exists() and doctors:
                    for i in range(2):
                        MedicalRecord.objects.create(
                            patient=user,
                            practitioner=doctors[i % len(doctors)],
                            record_date=timezone.now() - timedelta(days=random.randint(7, 30)),
                            chief_complaint=f'病患主訴{["身體不適，需要檢查", "定期回診追蹤"][i]}。',
                            objective_findings=f'生命徵象穩定，意識清楚。',
                            assessment=pdata['primary_diagnosis'],
                            plan='持續觀察，定期追蹤。',
                        )
                    self.stdout.write(f'  → 建立醫療記錄: 2筆')
                
                # 2. 生命徵象
                if not VitalSigns.objects.filter(patient=user).exists() and nurses:
                    for i in range(5):
                        VitalSigns.objects.create(
                            patient=user,
                            recorded_by=nurses[i % len(nurses)],
                            recorded_at=timezone.now() - timedelta(days=i),
                            systolic_bp=random.randint(115, 145),
                            diastolic_bp=random.randint(70, 90),
                            heart_rate=random.randint(68, 88),
                            respiratory_rate=random.randint(16, 20),
                            temperature=round(random.uniform(36.3, 37.2), 1),
                            spo2=random.randint(95, 99),
                            weight=round(random.uniform(52, 72), 1),
                            height=random.randint(155, 172),
                        )
                    self.stdout.write(f'  → 建立生命徵象: 5筆')
                
                # 3. 用藥記錄
                if not Medication.objects.filter(patient=user).exists() and doctors:
                    medications = [
                        ('Aspirin 100mg', 'qd', '抗血小板'),
                        ('Metformin 500mg', 'bid', '降血糖'),
                    ]
                    for med_name, freq, indication in medications:
                        Medication.objects.create(
                            patient=user,
                            prescribed_by=doctors[0],
                            medication_name=med_name,
                            dosage='1 tab',
                            frequency=freq,
                            route='PO',
                            start_date=timezone.now() - timedelta(days=60),
                            indication=indication,
                            status='active',
                        )
                    self.stdout.write(f'  → 建立用藥記錄: 2筆')
                
                # 4. 照護記錄
                if not CareRecord.objects.filter(patient=user).exists() and caregivers:
                    for i in range(3):
                        CareRecord.objects.create(
                            patient=user,
                            caregiver=record.caregiver,
                            record_date=timezone.now() - timedelta(days=i),
                            activity_type=['bathing', 'feeding', 'mobility'][i % 3],
                            description='協助完成日常活動',
                            patient_response='病患配合度良好',
                            duration_minutes=30,
                        )
                    self.stdout.write(f'  → 建立照護記錄: 3筆')
                
                updated_count += 1
                
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'⚠ 找不到使用者: {username}'))
                continue
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ 更新 {username} 時發生錯誤: {str(e)}'))
                continue
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS(f'完成！已更新 {updated_count} 位病患資料'))
        self.stdout.write(self.style.SUCCESS('='*60))
