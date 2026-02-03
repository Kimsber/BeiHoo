from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, datetime
from account.models import User
from clinical.models import (
    PatientRecord, MedicalRecord, VitalSigns, 
    Medication, MedicationAdministration, NursingNote,
    CarePlan, CarePlanGoal, CareRecord, IncidentReport,
    RehabPlan, RehabSession
)
import random


class Command(BaseCommand):
    help = '建立臨床管理測試資料'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('開始建立測試資料...'))
        
        # 1. 建立案管師 (Case Managers)
        case_managers = []
        for i in range(1, 4):
            user, created = User.objects.get_or_create(
                username=f'casemanager{i}',
                defaults={
                    'email': f'casemanager{i}@beihoo.com',
                    'first_name': f'案管師{i}',
                    'last_name': '李',
                    'role': 'case_manager',
                    'phone_number': f'0912-345-{600+i:03d}',
                }
            )
            if created:
                user.set_password('test1234')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'✓ 建立案管師: {user.username}'))
            case_managers.append(user)

        # 2. 建立照顧者 (Caregivers)
        caregivers = []
        for i in range(1, 6):
            user, created = User.objects.get_or_create(
                username=f'caregiver{i}',
                defaults={
                    'email': f'caregiver{i}@beihoo.com',
                    'first_name': f'照顧員{i}',
                    'last_name': '陳',
                    'role': 'caregiver',
                    'phone_number': f'0912-345-{700+i:03d}',
                }
            )
            if created:
                user.set_password('test1234')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'✓ 建立照顧者: {user.username}'))
            caregivers.append(user)

        # 3. 建立醫師 (Doctors)
        doctors = []
        for i in range(1, 4):
            user, created = User.objects.get_or_create(
                username=f'doctor{i}',
                defaults={
                    'email': f'doctor{i}@beihoo.com',
                    'first_name': f'醫師{i}',
                    'last_name': '王',
                    'role': 'doctor',
                    'phone_number': f'0912-345-{800+i:03d}',
                }
            )
            if created:
                user.set_password('test1234')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'✓ 建立醫師: {user.username}'))
            doctors.append(user)

        # 4. 建立護理師 (Nurses)
        nurses = []
        for i in range(1, 4):
            user, created = User.objects.get_or_create(
                username=f'nurse{i}',
                defaults={
                    'email': f'nurse{i}@beihoo.com',
                    'first_name': f'護理師{i}',
                    'last_name': '林',
                    'role': 'nurse',
                    'phone_number': f'0912-345-{900+i:03d}',
                }
            )
            if created:
                user.set_password('test1234')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'✓ 建立護理師: {user.username}'))
            nurses.append(user)

        # 5. 建立病患 (Patients)
        patients_data = [
            {
                'username': 'patient001',
                'first_name': '建國',
                'last_name': '張',
                'date_of_birth': '1945-05-15',
                'diagnosis': '中風後遺症、高血壓、糖尿病',
                'allergies': '盤尼西林',
                'emergency_contact': '張小華 (女兒)',
                'emergency_phone': '0912-345-001',
            },
            {
                'username': 'patient002',
                'first_name': '美玲',
                'last_name': '陳',
                'date_of_birth': '1950-08-20',
                'diagnosis': '帕金森氏症、骨質疏鬆',
                'allergies': '無',
                'emergency_contact': '陳大明 (兒子)',
                'emergency_phone': '0912-345-002',
            },
            {
                'username': 'patient003',
                'first_name': '志明',
                'last_name': '林',
                'date_of_birth': '1948-12-03',
                'diagnosis': '失智症、高血壓',
                'allergies': '阿斯匹靈',
                'emergency_contact': '林春花 (配偶)',
                'emergency_phone': '0912-345-003',
            },
            {
                'username': 'patient004',
                'first_name': '秀英',
                'last_name': '黃',
                'date_of_birth': '1952-03-25',
                'diagnosis': '心臟病、糖尿病',
                'allergies': '無',
                'emergency_contact': '黃大雄 (兒子)',
                'emergency_phone': '0912-345-004',
            },
            {
                'username': 'patient005',
                'first_name': '文雄',
                'last_name': '吳',
                'date_of_birth': '1947-07-10',
                'diagnosis': '脊椎損傷、輪椅使用者',
                'allergies': '無',
                'emergency_contact': '吳淑芬 (配偶)',
                'emergency_phone': '0912-345-005',
            },
            {
                'username': 'patient006',
                'first_name': '麗華',
                'last_name': '劉',
                'date_of_birth': '1955-11-18',
                'diagnosis': '類風濕性關節炎',
                'allergies': '海鮮',
                'emergency_contact': '劉俊傑 (兒子)',
                'emergency_phone': '0912-345-006',
            },
        ]

        patient_records = []
        for idx, pdata in enumerate(patients_data):
            # 建立使用者
            user, created = User.objects.get_or_create(
                username=pdata['username'],
                defaults={
                    'email': f"{pdata['username']}@patient.com",
                    'first_name': pdata['first_name'],
                    'last_name': pdata['last_name'],
                    'role': 'patient',
                    'phone_number': f'0912-111-{idx+1:03d}',
                    'date_of_birth': pdata['date_of_birth'],
                }
            )
            if created:
                user.set_password('test1234')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'✓ 建立病患: {user.username} ({user.get_full_name()})'))

            # 建立病患記錄
            record, created = PatientRecord.objects.get_or_create(
                patient=user,
                defaults={
                    'medical_record_number': f'MRN{2024000 + idx + 1}',
                    'primary_diagnosis': pdata['diagnosis'],
                    'allergies': pdata['allergies'],
                    'emergency_contact_name': pdata['emergency_contact'],
                    'emergency_contact_phone': pdata['emergency_phone'],
                    'case_manager': case_managers[idx % len(case_managers)],
                    'caregiver': caregivers[idx % len(caregivers)],
                    'notes': f'入院日期: {(timezone.now() - timedelta(days=random.randint(30, 180))).strftime("%Y-%m-%d")}',
                }
            )
            if created:
                self.stdout.write(f'  → 建立病患記錄: {record.medical_record_number}')
            patient_records.append(record)

        # 6. 建立醫療記錄 (Medical Records)
        self.stdout.write(self.style.WARNING('\n建立醫療記錄...'))
        soap_templates = [
            {
                'chief_complaint': '病患主訴頭暈、疲倦，昨晚睡眠品質不佳。',
                'objective_findings': 'BP: 145/90 mmHg, P: 82 bpm, 意識清楚，四肢活動正常。',
                'assessment': '血壓偏高，需密切監測。疲倦可能與睡眠不足有關。',
                'plan': '1. 調整降壓藥物劑量\n2. 建議睡前放鬆運動\n3. 一週後追蹤'
            },
            {
                'chief_complaint': '病患表示右膝疼痛，行走不便。',
                'objective_findings': '右膝關節輕微腫脹，壓痛(+)，活動度受限。',
                'assessment': '可能為退化性關節炎急性發作。',
                'plan': '1. 給予止痛藥物\n2. 建議休息、冰敷\n3. 轉介復健科'
            },
            {
                'chief_complaint': '病患主訴胸悶、呼吸稍喘。',
                'objective_findings': 'BP: 135/85, P: 95, SpO2: 94%, 呼吸音清晰。',
                'assessment': '可能與心臟功能不佳相關，需進一步檢查。',
                'plan': '1. 安排心電圖檢查\n2. 給予氧氣支持\n3. 持續監測生命徵象'
            },
        ]

        for record in patient_records[:4]:
            for i in range(random.randint(2, 4)):
                soap = soap_templates[i % len(soap_templates)]
                MedicalRecord.objects.create(
                    patient=record.patient,
                    practitioner=doctors[i % len(doctors)],
                    record_date=timezone.now() - timedelta(days=random.randint(1, 30)),
                    chief_complaint=soap['chief_complaint'],
                    objective_findings=soap['objective_findings'],
                    assessment=soap['assessment'],
                    plan=soap['plan'],
                )
        self.stdout.write(f'  ✓ 建立 {MedicalRecord.objects.count()} 筆醫療記錄')

        # 7. 建立生命徵象 (Vital Signs)
        self.stdout.write(self.style.WARNING('\n建立生命徵象記錄...'))
        for record in patient_records:
            for i in range(7):  # 一週的記錄
                VitalSigns.objects.create(
                    patient=record.patient,
                    recorded_by=nurses[i % len(nurses)],
                    recorded_at=timezone.now() - timedelta(days=i),
                    systolic_bp=random.randint(110, 150),
                    diastolic_bp=random.randint(65, 95),
                    heart_rate=random.randint(65, 95),
                    respiratory_rate=random.randint(16, 22),
                    temperature=round(random.uniform(36.2, 37.5), 1),
                    spo2=random.randint(94, 99),
                    weight=round(random.uniform(50, 75), 1),
                    height=random.randint(150, 175),
                )
        self.stdout.write(f'  ✓ 建立 {VitalSigns.objects.count()} 筆生命徵象記錄')

        # 8. 建立用藥記錄 (Medications)
        self.stdout.write(self.style.WARNING('\n建立用藥記錄...'))
        medications_list = [
            ('Amlodipine 5mg', 'qd', '降血壓'),
            ('Metformin 500mg', 'bid', '降血糖'),
            ('Aspirin 100mg', 'qd', '抗血小板'),
            ('Atorvastatin 10mg', 'qhs', '降血脂'),
        ]

        for record in patient_records[:4]:
            for med_name, freq, indication in medications_list[:random.randint(2, 4)]:
                med = Medication.objects.create(
                    patient=record.patient,
                    prescribed_by=doctors[0],
                    medication_name=med_name,
                    dosage='1 tab',
                    frequency=freq,
                    route='PO',
                    start_date=timezone.now() - timedelta(days=30),
                    indication=indication,
                )
                # 建立給藥記錄
                for i in range(3):
                    MedicationAdministration.objects.create(
                        medication=med,
                        scheduled_time=timezone.now() - timedelta(days=i),
                        administered_time=timezone.now() - timedelta(days=i),
                        administered_by=nurses[i % len(nurses)],
                        status='administered',
                        notes='按時給藥',
                    )
        self.stdout.write(f'  ✓ 建立 {Medication.objects.count()} 筆用藥記錄')
        self.stdout.write(f'  ✓ 建立 {MedicationAdministration.objects.count()} 筆給藥記錄')

        # 9. 建立護理記錄 (Nursing Notes)
        self.stdout.write(self.style.WARNING('\n建立護理記錄...'))
        nursing_templates = [
            {
                'assessment': '意識清楚，生命徵象穩定，皮膚完整性良好。',
                'intervention': '協助翻身、拍背，更換床單，給予口腔護理。',
                'evaluation': '病患舒適度改善，無壓瘡跡象。'
            },
            {
                'assessment': '右側肢體無力，需協助移位，進食吞嚥功能尚可。',
                'intervention': '協助進食、採半坐臥姿，執行肢體被動運動。',
                'evaluation': '進食量約70%，無嗆咳情形。'
            },
        ]

        for record in patient_records[:3]:
            for i in range(random.randint(2, 3)):
                template = nursing_templates[i % len(nursing_templates)]
                NursingNote.objects.create(
                    patient=record.patient,
                    nurse=nurses[i % len(nurses)],
                    note_datetime=timezone.now() - timedelta(days=i*2),
                    note_type='assessment',
                    assessment=template['assessment'],
                    intervention=template['intervention'],
                    evaluation=template['evaluation'],
                )
        self.stdout.write(f'  ✓ 建立 {NursingNote.objects.count()} 筆護理記錄')

        # 10. 建立照護計畫 (Care Plans)
        self.stdout.write(self.style.WARNING('\n建立照護計畫...'))
        for record in patient_records[:3]:
            care_plan = CarePlan.objects.create(
                patient=record.patient,
                case_manager=case_managers[0],
                title=f'{record.patient.get_full_name()} 照護計畫',
                description='長期照護計畫，包含日常生活照護、復健訓練、用藥管理等。',
                period_start=timezone.now() - timedelta(days=30),
                status='active',
            )
            
            # 建立目標
            goals = [
                '透過每日復健運動，提升肢體活動度，改善活動能力',
                '規律用藥，定期監測生命徵象，穩定慢性病控制',
                '環境安全評估，使用輔具，預防跌倒',
            ]
            for goal_desc in goals:
                CarePlanGoal.objects.create(
                    care_plan=care_plan,
                    description=goal_desc,
                    target_date=timezone.now() + timedelta(days=90),
                    achievement_status='in_progress',
                )
        self.stdout.write(f'  ✓ 建立 {CarePlan.objects.count()} 筆照護計畫')
        self.stdout.write(f'  ✓ 建立 {CarePlanGoal.objects.count()} 筆照護目標')

        # 11. 建立照護記錄 (Care Records)
        self.stdout.write(self.style.WARNING('\n建立照護記錄...'))
        for record in patient_records:
            activity_types = ['bathing', 'dressing', 'feeding', 'mobility', 'toileting']
            for i in range(5):
                activity = activity_types[i % len(activity_types)]
                CareRecord.objects.create(
                    patient=record.patient,
                    caregiver=caregivers[i % len(caregivers)],
                    record_date=timezone.now() - timedelta(days=i),
                    activity_type=activity,
                    duration_minutes=30,
                    description=f'日常照護執行順利，病患配合度佳。' if i % 2 == 0 else '病患情緒穩定，食欲正常。',
                    patient_response='病患反應良好',
                )
        self.stdout.write(f'  ✓ 建立 {CareRecord.objects.count()} 筆照護記錄')

        # 12. 建立事件報告 (Incident Reports)
        self.stdout.write(self.style.WARNING('\n建立事件報告...'))
        incidents = [
            {
                'type': 'fall',
                'severity': 'minor',
                'description': '病患在行走至浴室途中滑倒，立即扶起。',
                'action_taken': '協助病患回床休息，檢查無明顯外傷，持續觀察。',
            },
            {
                'type': 'medication_error',
                'severity': 'moderate',
                'description': '發現早上用藥時間延遲30分鐘給藥。',
                'action_taken': '立即給藥，向主治醫師回報，加強給藥時間管理。',
            },
        ]

        for idx, incident in enumerate(incidents):
            report = IncidentReport.objects.create(
                patient=patient_records[idx].patient,
                reported_by=caregivers[idx % len(caregivers)],
                incident_datetime=timezone.now() - timedelta(days=random.randint(5, 15)),
                incident_type=incident['type'],
                severity=incident['severity'],
                description=incident['description'],
                immediate_action=incident['action_taken'],
                status='resolved',
            )
            report.notified_staff.add(case_managers[0])
        self.stdout.write(f'  ✓ 建立 {IncidentReport.objects.count()} 筆事件報告')

        # 13. 建立復健計畫 (Rehab Plans)
        self.stdout.write(self.style.WARNING('\n建立復健計畫...'))
        for record in patient_records[:3]:
            rehab_plan = RehabPlan.objects.create(
                patient=record.patient,
                therapist=User.objects.filter(role='therapist').first() or doctors[0],
                plan_name=f'{record.patient.get_full_name()} 物理治療計畫',
                description='物理治療計畫，包含關節活動度訓練、肌力訓練、步態訓練',
                goals='改善肢體活動度、增強肌力、平衡訓練',
                start_date=timezone.now() - timedelta(days=14),
                sessions_per_week=3,
                duration_weeks=4,
                status='active',
            )
            
            # 建立療程記錄
            for i in range(3):
                RehabSession.objects.create(
                    rehab_plan=rehab_plan,
                    session_date=timezone.now() - timedelta(days=i*2),
                    duration_minutes=30,
                    activities_performed='關節活動度訓練、肌力訓練、步態訓練',
                    patient_response='病患配合度佳，活動度有進步。',
                    notes='療程順利完成',
                )
        self.stdout.write(f'  ✓ 建立 {RehabPlan.objects.count()} 筆復健計畫')
        self.stdout.write(f'  ✓ 建立 {RehabSession.objects.count()} 筆療程記錄')

        # 統計摘要
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('測試資料建立完成！'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'案管師: {len(case_managers)} 位')
        self.stdout.write(f'照顧者: {len(caregivers)} 位')
        self.stdout.write(f'醫師: {len(doctors)} 位')
        self.stdout.write(f'護理師: {len(nurses)} 位')
        self.stdout.write(f'病患: {len(patient_records)} 位')
        self.stdout.write(f'醫療記錄: {MedicalRecord.objects.count()} 筆')
        self.stdout.write(f'生命徵象: {VitalSigns.objects.count()} 筆')
        self.stdout.write(f'用藥記錄: {Medication.objects.count()} 筆')
        self.stdout.write(f'給藥記錄: {MedicationAdministration.objects.count()} 筆')
        self.stdout.write(f'護理記錄: {NursingNote.objects.count()} 筆')
        self.stdout.write(f'照護計畫: {CarePlan.objects.count()} 筆')
        self.stdout.write(f'照護目標: {CarePlanGoal.objects.count()} 筆')
        self.stdout.write(f'照護記錄: {CareRecord.objects.count()} 筆')
        self.stdout.write(f'事件報告: {IncidentReport.objects.count()} 筆')
        self.stdout.write(f'復健計畫: {RehabPlan.objects.count()} 筆')
        self.stdout.write(f'療程記錄: {RehabSession.objects.count()} 筆')
        self.stdout.write(self.style.SUCCESS('\n所有帳號密碼皆為: test1234'))
        self.stdout.write(self.style.SUCCESS('='*60))
