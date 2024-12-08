from datetime import datetime

class Patient:
    def __init__(self, name, age, gender, phone, email=None, visit_reasons=None, symptoms=None, medical_history=None):
        self.name = name
        self.age = age
        self.gender = gender
        self.phone = phone
        self.email = email
        self.visit_date = datetime.now()
        self.visit_reasons = visit_reasons or []
        self.symptoms = symptoms or []
        self.medical_history = medical_history or []
        self.diagnoses = []
        self.treatment_plans = []
        self.future_notes = []
        
    def add_visit_reason(self, reason):
        if reason and reason not in self.visit_reasons:
            self.visit_reasons.append(reason)
            
    def add_symptom(self, symptom):
        if symptom and symptom not in self.symptoms:
            self.symptoms.append(symptom)
            
    def add_medical_history_item(self, item):
        if item and item not in self.medical_history:
            self.medical_history.append(item)
        
    def add_diagnosis(self, diagnosis):
        self.diagnoses.append({
            'date': datetime.now(),
            'findings': diagnosis
        })
        
    def add_treatment_plan(self, plan):
        self.treatment_plans.append({
            'date': datetime.now(),
            'plan': plan
        })
        
    def add_future_note(self, note):
        self.future_notes.append({
            'date': datetime.now(),
            'note': note
        })
        
    def to_dict(self):
        return {
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'phone': self.phone,
            'email': self.email,
            'visit_date': self.visit_date.strftime('%Y-%m-%d %H:%M'),
            'visit_reasons': self.visit_reasons,
            'symptoms': self.symptoms,
            'medical_history': self.medical_history,
            'diagnoses': self.diagnoses,
            'treatment_plans': self.treatment_plans,
            'future_notes': self.future_notes
        }
