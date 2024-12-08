from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
from dental_analyzer import DentalAnalyzer
from patient import Patient
from report_generator import ReportGenerator
import cv2
import numpy as np

# تحميل المتغيرات البيئية
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['REPORTS_FOLDER'] = 'reports'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'dcm'}

# التأكد من وجود المجلدات الضرورية
for folder in [app.config['UPLOAD_FOLDER'], app.config['REPORTS_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_image(image_path):
    try:
        # قراءة الصورة
        if image_path.lower().endswith('.dcm'):
            import pydicom
            ds = pydicom.dcmread(image_path)
            image = ds.pixel_array
            image = ((image - image.min()) * 255.0 / (image.max() - image.min())).astype(np.uint8)
        else:
            image = cv2.imread(image_path)
            
        if image is None:
            raise ValueError("فشل في قراءة الصورة")
            
        analyzer = DentalAnalyzer()
        results = analyzer.analyze_image(image)
        
        # إضافة نوع الصورة للنتائج
        results['image_type'] = 'xray' if image_path.lower().endswith('.dcm') else 'normal'
        
        return results
    except Exception as e:
        print(f"Error analyzing image: {str(e)}")
        return {
            'scores': {},
            'recommendations': ['عذراً، حدث خطأ أثناء تحليل الصورة. يرجى التأكد من جودة الصورة وإعادة المحاولة.'],
            'image_type': 'error'
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'images[]' not in request.files:
        return jsonify({'error': 'لم يتم اختيار أي صور'}), 400
    
    files = request.files.getlist('images[]')
    if not files or all(file.filename == '' for file in files):
        return jsonify({'error': 'لم يتم اختيار أي ملفات'}), 400

    # استخراج معلومات المريض من الطلب
    patient_data = request.form.to_dict()
    
    try:
        patient = Patient(
            name=patient_data.get('name', ''),
            age=int(patient_data.get('age', 0)) if patient_data.get('age') else 0,
            gender=patient_data.get('gender', ''),
            phone=patient_data.get('phone', ''),
            email=patient_data.get('email', ''),
            visit_reasons=patient_data.get('visit_reasons', '').split(',') if patient_data.get('visit_reasons') else [],
            symptoms=patient_data.get('symptoms', '').split(',') if patient_data.get('symptoms') else [],
            medical_history=patient_data.get('medical_history', '').split(',') if patient_data.get('medical_history') else []
        )
    except Exception as e:
        print(f"Error creating patient object: {str(e)}")
        patient = Patient("", 0, "", "", "")

    results = []
    analyzer = DentalAnalyzer()
    
    for file in files:
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # قراءة الصورة
                if filepath.lower().endswith('.dcm'):
                    import pydicom
                    ds = pydicom.dcmread(filepath)
                    image = ds.pixel_array
                    image = ((image - image.min()) * 255.0 / (image.max() - image.min())).astype(np.uint8)
                else:
                    image = cv2.imread(filepath)
                
                if image is None:
                    raise ValueError("فشل في قراءة الصورة")
                
                # تحليل الصورة مع معلومات المريض
                analysis_result = analyzer.analyze_image_and_symptoms(image, patient)
                analysis_result['filename'] = filename
                analysis_result['image_type'] = 'xray' if filepath.lower().endswith('.dcm') else 'normal'
                
                results.append(analysis_result)
                
            except Exception as e:
                print(f"Error processing file {file.filename}: {str(e)}")
                results.append({
                    'filename': file.filename,
                    'error': str(e),
                    'scores': {},
                    'recommendations': ['حدث خطأ أثناء تحليل هذه الصورة'],
                    'image_type': 'error'
                })
            finally:
                # تنظيف الملف المؤقت
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                    except:
                        pass

    return jsonify({'results': results})

@app.route('/generate_report', methods=['POST'])
def generate_report():
    try:
        data = request.get_json()
        
        # إنشاء كائن المريض
        patient = Patient(
            name=data['name'],
            age=int(data['age']),
            gender=data['gender'],
            phone=data['phone'],
            email=data.get('email', ''),
            visit_reasons=data.get('visit_reasons', []),
            symptoms=data.get('symptoms', []),
            medical_history=data.get('medical_history', [])
        )
        
        # إضافة التشخيص وخطة العلاج والملاحظات
        if data.get('diagnosis'):
            patient.add_diagnosis(data['diagnosis'])
        
        if data.get('treatment_plan'):
            patient.add_treatment_plan(data['treatment_plan'])
            
        if data.get('future_notes'):
            patient.add_future_note(data['future_notes'])
        
        # إنشاء التقرير
        report_generator = ReportGenerator()
        report_filename = report_generator.generate_report(
            patient=patient,
            analysis_results=data.get('analysis_results', []),
            output_dir=app.config['REPORTS_FOLDER']
        )
        
        if not report_filename:
            raise ValueError("فشل في إنشاء التقرير")
        
        return jsonify({
            'success': True,
            'report_url': f'/download_report/{os.path.basename(report_filename)}'
        })
        
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'حدث خطأ أثناء إنشاء التقرير: {str(e)}'
        }), 500

@app.route('/download_report/<filename>')
def download_report(filename):
    return send_file(
        os.path.join(app.config['REPORTS_FOLDER'], filename),
        as_attachment=True
    )

if __name__ == '__main__':
    app.run(debug=True, port=5010)
