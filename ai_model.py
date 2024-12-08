import numpy as np
import cv2
from typing import List, Dict

class DentalAIModel:
    def __init__(self):
        # القاموس للترجمة بين الإنجليزية والعربية
        self.condition_translations = {
            'cavity': 'تسوس',
            'gum_inflammation': 'التهاب لثة',
            'plaque': 'تراكم البلاك',
            'healthy': 'أسنان سليمة',
            'erosion': 'تآكل المينا',
            'sensitivity': 'حساسية الأسنان'
        }
        
    def preprocess_image(self, image):
        """تجهيز الصورة للتحليل"""
        # تحويل الصورة إلى المقاس المطلوب
        image = cv2.resize(image, (224, 224))
        return image
    
    def predict(self, image):
        """
        محاكاة تحليل الذكاء الاصطناعي باستخدام تحليل الصور التقليدي
        في المستقبل سيتم استبدال هذا بنموذج تعلم عميق حقيقي
        """
        # تحويل الصورة إلى تدرج الرمادي
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # تحويل الصورة إلى HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # حساب خصائص الصورة
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        # تحليل اللون للكشف عن مشاكل محتملة
        yellow_mask = cv2.inRange(hsv, np.array([20, 50, 50]), np.array([30, 255, 255]))
        red_mask = cv2.inRange(hsv, np.array([0, 50, 50]), np.array([10, 255, 255]))
        
        yellow_ratio = np.sum(yellow_mask > 0) / yellow_mask.size
        red_ratio = np.sum(red_mask > 0) / red_mask.size
        
        # تحديد الحالات المحتملة بناءً على التحليل
        results = []
        
        # تحليل التسوس (المناطق الداكنة)
        if brightness < 100:
            results.append({
                'condition': 'cavity',
                'confidence': min((120 - brightness) / 120 * 100, 95)
            })
        
        # تحليل البلاك (المناطق الصفراء)
        if yellow_ratio > 0.1:
            results.append({
                'condition': 'plaque',
                'confidence': min(yellow_ratio * 300, 90)
            })
        
        # تحليل التهاب اللثة (المناطق الحمراء)
        if red_ratio > 0.15:
            results.append({
                'condition': 'gum_inflammation',
                'confidence': min(red_ratio * 250, 85)
            })
        
        # تحليل تآكل المينا (التباين)
        if contrast > 60:
            results.append({
                'condition': 'erosion',
                'confidence': min(contrast * 1.5, 80)
            })
        
        # إذا لم يتم اكتشاف أي مشاكل، نفترض أن الأسنان سليمة
        if not results:
            results.append({
                'condition': 'healthy',
                'confidence': 95.0
            })
        
        # ترجمة النتائج إلى العربية للعرض
        translated_results = []
        for result in results:
            translated_results.append({
                'condition': self.condition_translations[result['condition']],
                'confidence': result['confidence']
            })
        
        return translated_results
    
    def get_recommendations(self, predictions: List[Dict]) -> List[str]:
        """توليد توصيات بناءً على التحليل"""
        recommendations = []
        
        for pred in predictions:
            condition = pred['condition']
            confidence = pred['confidence']
            
            if condition == 'تسوس' and confidence > 60:
                recommendations.append(
                    "يُنصح بزيارة طبيب الأسنان في أقرب وقت للكشف عن التسوس وعلاجه"
                )
            elif condition == 'التهاب لثة' and confidence > 50:
                recommendations.append(
                    "يُنصح باستخدام غسول الفم المضاد للبكتيريا وتحسين نظافة الفم"
                )
            elif condition == 'تراكم البلاك' and confidence > 40:
                recommendations.append(
                    "يُنصح بتنظيف الأسنان لدى طبيب الأسنان وتحسين عادات تنظيف الأسنان اليومية"
                )
            elif condition == 'تآكل المينا' and confidence > 50:
                recommendations.append(
                    "يُنصح بتجنب المشروبات الحمضية واستخدام معجون أسنان يحتوي على الفلورايد"
                )
            elif condition == 'حساسية الأسنان' and confidence > 50:
                recommendations.append(
                    "يُنصح باستخدام معجون أسنان مخصص للأسنان الحساسة وتجنب الأطعمة شديدة البرودة أو السخونة"
                )
        
        if not recommendations:
            recommendations.append(
                "أسنانك تبدو بصحة جيدة! استمر في العناية اليومية بنظافة فمك وأسنانك"
            )
        
        return recommendations
