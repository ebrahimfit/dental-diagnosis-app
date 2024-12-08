import cv2
import numpy as np

class DentalAnalyzer:
    def __init__(self):
        self.conditions = {
            'cavity': 'تسوس',
            'gum_inflammation': 'التهاب لثة',
            'plaque': 'تراكم البلاك',
            'erosion': 'تآكل المينا',
            'sensitivity': 'حساسية الأسنان',
            'overall_health': 'الصحة العامة'
        }
        
        self.symptom_conditions = {
            'ألم': ['cavity', 'sensitivity'],
            'نزيف': ['gum_inflammation'],
            'حساسية': ['sensitivity', 'erosion'],
            'تورم': ['gum_inflammation'],
            'رائحة': ['plaque', 'gum_inflammation'],
            'تغير لون': ['cavity', 'erosion']
        }

    def analyze_image_and_symptoms(self, image, patient):
        # تحليل الصورة
        image_analysis = self.analyze_image(image)
        
        # تعديل النتائج بناءً على الأعراض والتاريخ المرضي
        adjusted_scores = self._adjust_scores_based_on_patient(
            image_analysis['scores'],
            patient
        )
        
        # توليد توصيات محدثة
        recommendations = self._generate_recommendations(
            adjusted_scores,
            patient
        )
        
        return {
            'scores': adjusted_scores,
            'recommendations': recommendations
        }

    def analyze_image(self, image):
        try:
            # تحويل الصورة إلى تدرج الرمادي
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image

            # تحسين جودة الصورة
            gray = cv2.equalizeHist(gray)
            
            # تطبيق مرشح لتقليل الضوضاء
            gray = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # حساب الدرجات لكل حالة
            scores = {}
            
            # تحليل التسوس
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cavity_score = min(len(contours) / 100.0, 1.0)
            scores['cavity'] = cavity_score
            
            # تحليل التهاب اللثة
            edges = cv2.Canny(gray, 100, 200)
            inflammation_score = np.sum(edges > 0) / (gray.shape[0] * gray.shape[1])
            scores['gum_inflammation'] = min(inflammation_score * 2, 1.0)
            
            # تحليل تراكم البلاك
            blur = cv2.GaussianBlur(gray, (15, 15), 0)
            plaque_score = np.std(gray - blur) / 128.0
            scores['plaque'] = min(plaque_score * 2, 1.0)
            
            # تحليل تآكل المينا
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            erosion_score = np.std(laplacian) / 128.0
            scores['erosion'] = min(erosion_score * 2, 1.0)
            
            # تقدير الحساسية
            sensitivity_score = (cavity_score + erosion_score) / 2
            scores['sensitivity'] = sensitivity_score
            
            # تقييم الصحة العامة
            overall_health = 1.0 - np.mean([
                cavity_score,
                inflammation_score,
                plaque_score,
                erosion_score,
                sensitivity_score
            ])
            scores['overall_health'] = overall_health
            
            return {
                'scores': scores,
                'recommendations': self._generate_basic_recommendations(scores)
            }
            
        except Exception as e:
            print(f"Error in analyze_image: {str(e)}")
            return {
                'scores': {
                    'cavity': 0.0,
                    'gum_inflammation': 0.0,
                    'plaque': 0.0,
                    'erosion': 0.0,
                    'sensitivity': 0.0,
                    'overall_health': 0.0
                },
                'recommendations': ['عذراً، حدث خطأ أثناء تحليل الصورة. يرجى التأكد من جودة الصورة وإعادة المحاولة.']
            }

    def _adjust_scores_based_on_patient(self, scores, patient):
        adjusted_scores = scores.copy()
        
        # تعديل النتائج بناءً على الأعراض
        for symptom in patient.symptoms:
            if symptom in self.symptom_conditions:
                related_conditions = self.symptom_conditions[symptom]
                for condition in related_conditions:
                    # تخفيض درجة الصحة للحالات المرتبطة بالأعراض
                    adjusted_scores[condition] = min(
                        adjusted_scores[condition] * 0.8,
                        adjusted_scores[condition]
                    )
        
        # تعديل النتائج بناءً على العمر
        if patient.age > 60:
            # زيادة احتمالية مشاكل اللثة وتآكل المينا للمرضى الأكبر سناً
            adjusted_scores['gum_inflammation'] *= 0.9
            adjusted_scores['erosion'] *= 0.9
        elif patient.age < 18:
            # زيادة احتمالية التسوس للمرضى الأصغر سناً
            adjusted_scores['cavity'] *= 0.9
        
        # تعديل النتائج بناءً على أسباب الزيارة
        for reason in patient.visit_reasons:
            if 'ألم' in reason.lower():
                adjusted_scores['cavity'] *= 0.8
                adjusted_scores['sensitivity'] *= 0.8
            elif 'نزيف' in reason.lower():
                adjusted_scores['gum_inflammation'] *= 0.7
            elif 'رائحة' in reason.lower():
                adjusted_scores['plaque'] *= 0.8
                adjusted_scores['gum_inflammation'] *= 0.8
        
        # إعادة حساب الصحة العامة
        adjusted_scores['overall_health'] = sum(
            score for condition, score in adjusted_scores.items()
            if condition != 'overall_health'
        ) / (len(adjusted_scores) - 1)
        
        return adjusted_scores

    def _normalize_score(self, value, min_threshold, max_threshold):
        if value < min_threshold:
            return 1.0
        elif value > max_threshold:
            return 0.0
        else:
            return 1.0 - ((value - min_threshold) / (max_threshold - min_threshold))

    def _calculate_overall_health(self, brightness, contrast, edge_density):
        health_indicators = [
            self._normalize_score(1 - brightness, 0.3, 0.7),
            self._normalize_score(contrast, 0.2, 0.6),
            self._normalize_score(edge_density, 0.1, 0.4)
        ]
        return sum(health_indicators) / len(health_indicators)

    def _generate_recommendations(self, scores, patient=None):
        recommendations = []
        
        # توصيات بناءً على نتائج التحليل
        if scores['cavity'] < 0.7:
            recommendations.append("ينصح بزيارة طبيب الأسنان للكشف عن التسوس المحتمل")
        
        if scores['gum_inflammation'] < 0.7:
            recommendations.append("يُنصح باستخدام غسول الفم المضاد للبكتيريا وتحسين نظافة الفم")
        
        if scores['plaque'] < 0.6:
            recommendations.append("يجب تحسين تنظيف الأسنان باستخدام الفرشاة والخيط السني بانتظام")
        
        if scores['erosion'] < 0.7:
            recommendations.append("تجنب المشروبات الحمضية وتناول الأطعمة القاسية")
        
        if scores['sensitivity'] < 0.7:
            recommendations.append("استخدم معجون أسنان مخصص للأسنان الحساسة")
        
        if scores['overall_health'] < 0.6:
            recommendations.append("يُنصح بزيارة طبيب الأسنان لفحص شامل وتنظيف احترافي")
            
        # إضافة توصيات خاصة بناءً على معلومات المريض
        if patient:
            if patient.age > 60:
                recommendations.append("نظراً لعمرك، يُنصح بزيارة طبيب الأسنان كل 4-6 أشهر للفحص الدوري")
            elif patient.age < 18:
                recommendations.append("يُنصح بتجنب الحلويات والمشروبات الغازية وتنظيف الأسنان بعد كل وجبة")
            
            for symptom in patient.symptoms:
                if 'ألم' in symptom.lower():
                    recommendations.append("يُنصح بتجنب الأطعمة والمشروبات شديدة البرودة أو السخونة")
                elif 'نزيف' in symptom.lower():
                    recommendations.append("استخدم فرشاة أسنان ناعمة وتجنب الضغط الشديد أثناء التنظيف")
        
        if not recommendations:
            recommendations.append("صحة أسنانك جيدة! حافظ على روتين العناية اليومي")
        
        return recommendations

    def _generate_basic_recommendations(self, scores):
        recommendations = []
        
        # توصيات بناءً على نتائج التحليل
        if scores['cavity'] < 0.7:
            recommendations.append("ينصح بزيارة طبيب الأسنان للكشف عن التسوس المحتمل")
        
        if scores['gum_inflammation'] < 0.7:
            recommendations.append("يُنصح باستخدام غسول الفم المضاد للبكتيريا وتحسين نظافة الفم")
        
        if scores['plaque'] < 0.6:
            recommendations.append("يجب تحسين تنظيف الأسنان باستخدام الفرشاة والخيط السني بانتظام")
        
        if scores['erosion'] < 0.7:
            recommendations.append("تجنب المشروبات الحمضية وتناول الأطعمة القاسية")
        
        if scores['sensitivity'] < 0.7:
            recommendations.append("استخدم معجون أسنان مخصص للأسنان الحساسة")
        
        if scores['overall_health'] < 0.6:
            recommendations.append("يُنصح بزيارة طبيب الأسنان لفحص شامل وتنظيف احترافي")
        
        if not recommendations:
            recommendations.append("صحة أسنانك جيدة! حافظ على روتين العناية اليومي")
        
        return recommendations
