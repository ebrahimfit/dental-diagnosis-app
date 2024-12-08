from datetime import datetime
from report_generator import ReportGenerator
from dataclasses import dataclass

@dataclass
class Patient:
    name: str
    age: int
    gender: str
    phone: str
    email: str
    visit_date: datetime
    visit_reasons: list
    symptoms: list
    medical_history: list
    diagnoses: list
    treatment_plans: list
    future_notes: list

def create_test_report():
    # إنشاء بيانات مريض تجريبية
    patient = Patient(
        name="أحمد محمد علي",
        age=35,
        gender="ذكر",
        phone="0501234567",
        email="ahmed@example.com",
        visit_date=datetime.now(),
        visit_reasons=["ألم في الأسنان", "نزيف في اللثة"],
        symptoms=["ألم شديد عند تناول الطعام", "حساسية للبرودة"],
        medical_history=["ضغط دم مرتفع", "حساسية من البنسلين"],
        diagnoses=[
            {
                'date': datetime.now(),
                'findings': "تسوس عميق في الضرس العلوي الأيمن، والتهاب في اللثة المحيطة"
            }
        ],
        treatment_plans=[
            {
                'date': datetime.now(),
                'plan': "1. حشو الضرس المتسوس\n2. تنظيف وتلميع الأسنان\n3. علاج اللثة بالليزر"
            }
        ],
        future_notes=[
            {
                'date': datetime.now(),
                'note': "متابعة حالة اللثة بعد أسبوعين، وتقييم استجابة المريض للعلاج"
            }
        ]
    )

    # إنشاء نتائج تحليل تجريبية
    analysis_results = [
        {
            'filename': 'dental_xray_001.jpg',
            'image_type': 'xray',
            'scores': {
                'cavity': 0.75,
                'gum_inflammation': 0.60,
                'plaque': 0.40,
                'erosion': 0.30,
                'sensitivity': 0.65,
                'overall_health': 0.55
            },
            'recommendations': [
                "يجب علاج التسوس في الضرس العلوي الأيمن في أقرب وقت",
                "ينصح بتنظيف الأسنان مرتين يومياً",
                "استخدام معجون أسنان خاص بالأسنان الحساسة",
                "زيارة طبيب الأسنان للمتابعة بعد شهر"
            ]
        }
    ]

    # إنشاء مولد التقارير وإنشاء التقرير
    generator = ReportGenerator()
    report_path = generator.generate_report(patient, analysis_results, "reports")
    print(f"تم إنشاء التقرير في: {report_path}")

if __name__ == "__main__":
    # إنشاء مجلد التقارير إذا لم يكن موجوداً
    import os
    os.makedirs("reports", exist_ok=True)
    
    # إنشاء التقرير التجريبي
    create_test_report()
