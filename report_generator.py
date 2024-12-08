import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class ReportGenerator:
    def __init__(self):
        """تهيئة مولد التقارير"""
        # تهيئة الخطوط العربية
        pdfmetrics.registerFont(TTFont('Arabic', 'static/fonts/NotoSansArabic-Regular.ttf'))
        pdfmetrics.registerFont(TTFont('ArabicBold', 'static/fonts/NotoSansArabic-Bold.ttf'))
        
        # إنشاء أنماط النص
        self.arabic_style = ParagraphStyle(
            'Arabic',
            fontName='Arabic',
            fontSize=11,
            leading=16,
            alignment=1,  # center alignment
            rightIndent=0,
            leftIndent=0,
            spaceBefore=0,
            spaceAfter=0,
            textColor=colors.black,
        )
        
        self.arabic_bold_style = ParagraphStyle(
            'ArabicBold',
            fontName='ArabicBold',
            fontSize=14,
            leading=20,
            alignment=1,  # center alignment
            rightIndent=0,
            leftIndent=0,
            spaceBefore=6,
            spaceAfter=6,
            textColor=colors.black,
        )
        
        self.header_style = ParagraphStyle(
            'Header',
            fontName='ArabicBold',
            fontSize=18,
            leading=22,
            alignment=1,  # center alignment
            rightIndent=0,
            leftIndent=0,
            spaceBefore=12,
            spaceAfter=12,
            textColor=colors.HexColor('#1B4F72'),  # أزرق داكن
        )
        
        self.section_header_style = ParagraphStyle(
            'SectionHeader',
            fontName='ArabicBold',
            fontSize=14,
            leading=18,
            alignment=1,  # center alignment
            rightIndent=0,
            leftIndent=0,
            spaceBefore=8,
            spaceAfter=8,
            textColor=colors.HexColor('#2874A6'),  # أزرق فاتح
            borderColor=colors.HexColor('#2874A6'),
            borderWidth=1,
            borderPadding=5,
        )
        
    def _process_arabic_text(self, text):
        """معالجة النص العربي للعرض الصحيح"""
        if not text:
            return ""
        try:
            # تحويل النص إلى UTF-8
            text = str(text)
            # معالجة النص العربي
            reshaped_text = arabic_reshaper.reshape(text)
            # تحويل اتجاه النص
            bidi_text = get_display(reshaped_text)
            return bidi_text
        except Exception as e:
            print(f"Error processing Arabic text: {str(e)}")
            return text

    def _process_patient_data(self, patient):
        """معالجة بيانات المريض للعرض الصحيح في PDF"""
        data = {
            'name': self._process_arabic_text(patient.name),
            'age': patient.age,
            'gender': self._process_arabic_text(patient.gender),
            'phone': patient.phone,
            'email': patient.email,
            'visit_date': patient.visit_date.strftime('%Y-%m-%d %H:%M'),
            'visit_reasons': [self._process_arabic_text(reason) for reason in patient.visit_reasons if reason],
            'symptoms': [self._process_arabic_text(symptom) for symptom in patient.symptoms if symptom],
            'medical_history': [self._process_arabic_text(item) for item in patient.medical_history if item],
            'diagnoses': [],
            'treatment_plans': [],
            'future_notes': []
        }
        
        # معالجة التشخيصات
        for diagnosis in patient.diagnoses:
            data['diagnoses'].append({
                'date': diagnosis['date'].strftime('%Y-%m-%d %H:%M'),
                'findings': self._process_arabic_text(diagnosis['findings'])
            })
            
        # معالجة خطط العلاج
        for plan in patient.treatment_plans:
            data['treatment_plans'].append({
                'date': plan['date'].strftime('%Y-%m-%d %H:%M'),
                'plan': self._process_arabic_text(plan['plan'])
            })
            
        # معالجة الملاحظات المستقبلية
        for note in patient.future_notes:
            data['future_notes'].append({
                'date': note['date'].strftime('%Y-%m-%d %H:%M'),
                'note': self._process_arabic_text(note['note'])
            })
            
        return data

    def _process_analysis_results(self, results):
        """معالجة نتائج التحليل للعرض الصحيح في PDF"""
        processed_results = []
        for result in results:
            processed_result = {
                'filename': self._process_arabic_text(result['filename']),
                'image_type': result['image_type'],
                'scores': result['scores'],
                'recommendations': [
                    self._process_arabic_text(rec) for rec in result['recommendations']
                ]
            }
            processed_results.append(processed_result)
        return processed_results
    
    def generate_report(self, patient, analysis_results, output_dir):
        """إنشاء تقرير PDF"""
        try:
            # معالجة البيانات للعرض الصحيح
            processed_patient = self._process_patient_data(patient)
            processed_results = self._process_analysis_results(analysis_results)
            
            # إنشاء اسم الملف
            filename = f"dental_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            output_path = os.path.join(output_dir, filename)
            
            # إعداد مستند PDF
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=40,
                encoding='UTF-8'
            )
            
            # إنشاء محتوى التقرير
            story = []
            
            # إضافة الشعار والعنوان
            story.append(Paragraph(self._process_arabic_text("عيادة دكتور محمد"), self.header_style))
            story.append(Paragraph(self._process_arabic_text("أخصائي طب وجراحة الفم والأسنان"), self.arabic_bold_style))
            story.append(Spacer(1, 20))
            
            # إضافة معلومات التقرير
            report_info = self._process_arabic_text(f"تقرير التشخيص الطبي - {processed_patient['visit_date']}")
            story.append(Paragraph(report_info, self.section_header_style))
            story.append(Spacer(1, 20))
            
            # إضافة معلومات المريض
            story.append(Paragraph(self._process_arabic_text("معلومات المريض"), self.section_header_style))
            story.append(Spacer(1, 10))
            
            patient_data = [
                [Paragraph(self._process_arabic_text("الاسم:"), self.arabic_bold_style),
                 Paragraph(self._process_arabic_text(processed_patient['name']), self.arabic_style)],
                [Paragraph(self._process_arabic_text("العمر:"), self.arabic_bold_style),
                 Paragraph(str(processed_patient['age']), self.arabic_style)],
                [Paragraph(self._process_arabic_text("الجنس:"), self.arabic_bold_style),
                 Paragraph(self._process_arabic_text(processed_patient['gender']), self.arabic_style)],
                [Paragraph(self._process_arabic_text("رقم الهاتف:"), self.arabic_bold_style),
                 Paragraph(processed_patient['phone'], self.arabic_style)]
            ]
            
            if processed_patient['email']:
                patient_data.append([
                    Paragraph(self._process_arabic_text("البريد الإلكتروني:"), self.arabic_bold_style),
                    Paragraph(processed_patient['email'], self.arabic_style)
                ])
            
            # إنشاء جدول معلومات المريض
            patient_table = Table(patient_data, colWidths=[120, 360])
            patient_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F4F6F7')),  # رمادي فاتح
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            
            story.append(patient_table)
            story.append(Spacer(1, 20))
            
            # إضافة سبب الزيارة والأعراض
            if processed_patient['visit_reasons'] or processed_patient['symptoms']:
                story.append(Paragraph(self._process_arabic_text("سبب الزيارة والأعراض"), self.section_header_style))
                story.append(Spacer(1, 10))
                
                visit_data = []
                if processed_patient['visit_reasons']:
                    visit_data.append([
                        Paragraph(self._process_arabic_text("سبب الزيارة:"), self.arabic_bold_style),
                        Paragraph(self._process_arabic_text(" • " + "\n • ".join(processed_patient['visit_reasons'])), self.arabic_style)
                    ])
                
                if processed_patient['symptoms']:
                    visit_data.append([
                        Paragraph(self._process_arabic_text("الأعراض:"), self.arabic_bold_style),
                        Paragraph(self._process_arabic_text(" • " + "\n • ".join(processed_patient['symptoms'])), self.arabic_style)
                    ])
                
                visit_table = Table(visit_data, colWidths=[120, 360])
                visit_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F4F6F7')),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ]))
                
                story.append(visit_table)
                story.append(Spacer(1, 20))
            
            # إضافة التاريخ الطبي
            if processed_patient['medical_history']:
                story.append(Paragraph(self._process_arabic_text("التاريخ الطبي"), self.section_header_style))
                story.append(Spacer(1, 10))
                
                history_text = " • " + "\n • ".join(processed_patient['medical_history'])
                story.append(Paragraph(self._process_arabic_text(history_text), self.arabic_style))
                story.append(Spacer(1, 20))
            
            # إضافة نتائج التحليل
            if processed_results:
                story.append(Paragraph(self._process_arabic_text("نتائج التحليل والتشخيص"), self.section_header_style))
                story.append(Spacer(1, 10))
                
                for result in processed_results:
                    # إضافة اسم الملف
                    story.append(Paragraph(
                        self._process_arabic_text(f"تحليل الصورة: {result['filename']}"),
                        self.arabic_bold_style
                    ))
                    story.append(Spacer(1, 5))
                    
                    # إضافة الدرجات
                    scores_data = [
                        [Paragraph(self._process_arabic_text("الحالة"), self.arabic_bold_style),
                         Paragraph(self._process_arabic_text("الدرجة"), self.arabic_bold_style),
                         Paragraph(self._process_arabic_text("التقييم"), self.arabic_bold_style)]
                    ]
                    
                    for condition, score in result['scores'].items():
                        condition_name = {
                            'cavity': 'تسوس',
                            'gum_inflammation': 'التهاب لثة',
                            'plaque': 'تراكم البلاك',
                            'erosion': 'تآكل المينا',
                            'sensitivity': 'حساسية الأسنان',
                            'overall_health': 'الصحة العامة'
                        }.get(condition, condition)
                        
                        # تحديد التقييم بناءً على الدرجة
                        score_value = int(score * 100)
                        if score_value >= 80:
                            assessment = "خطير"
                            color = colors.red
                        elif score_value >= 60:
                            assessment = "متوسط"
                            color = colors.orange
                        elif score_value >= 40:
                            assessment = "مقبول"
                            color = colors.yellow
                        else:
                            assessment = "جيد"
                            color = colors.green
                        
                        scores_data.append([
                            Paragraph(self._process_arabic_text(condition_name), self.arabic_style),
                            Paragraph(f"{score_value}%", self.arabic_style),
                            Paragraph(self._process_arabic_text(assessment), 
                                    ParagraphStyle('Assessment', parent=self.arabic_style, textColor=color))
                        ])
                    
                    scores_table = Table(scores_data, colWidths=[200, 100, 180])
                    scores_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F4F6F7')),
                        ('LEFTPADDING', (0, 0), (-1, -1), 8),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                        ('TOPPADDING', (0, 0), (-1, -1), 5),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ]))
                    
                    story.append(scores_table)
                    story.append(Spacer(1, 15))
                    
                    # إضافة التوصيات
                    if result['recommendations']:
                        story.append(Paragraph(self._process_arabic_text("التوصيات:"), self.arabic_bold_style))
                        story.append(Spacer(1, 5))
                        for rec in result['recommendations']:
                            story.append(Paragraph(
                                self._process_arabic_text(f"• {rec}"),
                                self.arabic_style
                            ))
                        story.append(Spacer(1, 15))
            
            # إضافة خطة العلاج
            if processed_patient['treatment_plans']:
                story.append(Paragraph(self._process_arabic_text("خطة العلاج"), self.section_header_style))
                story.append(Spacer(1, 10))
                
                for plan in processed_patient['treatment_plans']:
                    story.append(Paragraph(
                        self._process_arabic_text(plan['plan']),
                        self.arabic_style
                    ))
                story.append(Spacer(1, 20))
            
            # إضافة ملاحظات المتابعة
            if processed_patient['future_notes']:
                story.append(Paragraph(self._process_arabic_text("ملاحظات المتابعة"), self.section_header_style))
                story.append(Spacer(1, 10))
                
                for note in processed_patient['future_notes']:
                    story.append(Paragraph(
                        self._process_arabic_text(note['note']),
                        self.arabic_style
                    ))
                story.append(Spacer(1, 20))
            
            # إضافة التذييل
            story.append(Spacer(1, 30))
            footer_text = f"""
            {self._process_arabic_text('تم إنشاء هذا التقرير بواسطة نظام التحليل الذكي للأسنان')}
            {self._process_arabic_text('تاريخ التقرير:')} {datetime.now().strftime('%Y-%m-%d %H:%M')}
            
            {self._process_arabic_text('ملاحظة: هذا التقرير إرشادي ويجب مراجعة الطبيب المختص للتشخيص النهائي')}
            """
            footer = Paragraph(footer_text, ParagraphStyle(
                'Footer',
                parent=self.arabic_style,
                alignment=1,  # center alignment
                textColor=colors.grey
            ))
            story.append(footer)
            
            # إنشاء التقرير
            doc.build(story)
            
            return output_path
            
        except Exception as e:
            print(f"Error generating PDF report: {str(e)}")
            return None
