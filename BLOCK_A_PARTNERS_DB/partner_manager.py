"""
МЕНЕДЖЕР ДЛЯ РАБОТЫ С ПАРТНЕРАМИ
CRUD операции и бизнес-логика
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from .models import db, Partner, PartnerVerificationLog

class PartnerManager:
    """Менеджер для работы с партнерами"""
    
    @staticmethod
    def create_partner(data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание нового партнера"""
        try:
            # Генерация кода партнера
            from datetime import datetime
            import random
            
            date_str = datetime.now().strftime('%y%m%d')
            random_num = random.randint(1000, 9999)
            partner_code = f"P-{date_str}-{random_num}"
            
            partner = Partner(
                partner_code=partner_code,
                company_name=data['company_name'],
                legal_form=data.get('legal_form', 'ООО'),
                inn=data['inn'],
                contact_person=data['contact_person'],
                phone=data['phone'],
                email=data['email'],
                verification_status='pending',
                is_active=False
            )
            
            db.session.add(partner)
            db.session.commit()
            
            return {
                'success': True,
                'partner': partner.to_dict(),
                'message': 'Партнер создан успешно'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Ошибка создания партнера: {str(e)}'
            }
    
    @staticmethod
    def update_partner(partner_code: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Обновление данных партнера"""
        try:
            partner = Partner.query.filter_by(partner_code=partner_code).first()
            if not partner:
                return {'success': False, 'error': 'Партнер не найден'}
            
            # Поля, которые можно обновлять
            updatable_fields = [
                'company_name', 'contact_person', 'phone', 'email', 'website',
                'main_category', 'specializations', 'services', 'regions', 'cities',
                'radius_km', 'settings'
            ]
            
            for field in updatable_fields:
                if field in data:
                    setattr(partner, field, data[field])
            
            partner.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'success': True,
                'partner': partner.to_dict(),
                'message': 'Данные партнера обновлены'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Ошибка обновления партнера: {str(e)}'
            }
    
    @staticmethod
    def verify_partner(partner_code: str, verified_by: str = 'system') -> Dict[str, Any]:
        """Верификация партнера"""
        try:
            partner = Partner.query.filter_by(partner_code=partner_code).first()
            if not partner:
                return {'success': False, 'error': 'Партнер не найден'}
            
            partner.verification_status = 'verified'
            partner.verification_date = datetime.utcnow()
            partner.verified_by = verified_by
            partner.is_active = True
            
            # Логирование
            log = PartnerVerificationLog(
                partner_id=partner.id,
                partner_code=partner_code,
                action='manual_verification',
                status='success',
                details={'verified_by': verified_by},
                performed_by=verified_by
            )
            db.session.add(log)
            
            db.session.commit()
            
            return {
                'success': True,
                'partner': partner.to_dict(),
                'message': 'Партнер успешно верифицирован'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Ошибка верификации партнера: {str(e)}'
            }
    
    @staticmethod
    def search_partners(criteria: Dict[str, Any], page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Поиск партнеров по критериям"""
        try:
            query = Partner.query.filter(
                Partner.verification_status == 'verified',
                Partner.is_active == True
            )
            
            # Применение фильтров
            if criteria.get('region'):
                query = query.filter(Partner.regions.contains([criteria['region']]))
            
            if criteria.get('specializations'):
                query = query.filter(
                    Partner.specializations.overlap(criteria['specializations'])
                )
            
            if criteria.get('main_category'):
                query = query.filter(Partner.main_category == criteria['main_category'])
            
            if criteria.get('min_rating'):
                query = query.filter(Partner.rating >= criteria['min_rating'])
            
            # Сортировка
            sort_by = criteria.get('sort_by', 'rating')
            sort_order = criteria.get('sort_order', 'desc')
            
            if sort_by == 'rating':
                if sort_order == 'desc':
                    query = query.order_by(Partner.rating.desc())
                else:
                    query = query.order_by(Partner.rating.asc())
            elif sort_by == 'response_rate':
                if sort_order == 'desc':
                    query = query.order_by(Partner.response_rate.desc())
                else:
                    query = query.order_by(Partner.response_rate.asc())
            else:
                query = query.order_by(Partner.created_at.desc())
            
            # Пагинация
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            
            return {
                'success': True,
                'partners': [p.to_dict() for p in pagination.items],
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'pages': pagination.pages
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка поиска партнеров: {str(e)}'
            }
    
    @staticmethod
    def get_partner_stats() -> Dict[str, Any]:
        """Получение статистики по партнерам"""
        try:
            total = Partner.query.count()
            verified = Partner.query.filter_by(verification_status='verified').count()
            active = Partner.query.filter_by(is_active=True).count()
            pending = Partner.query.filter_by(verification_status='pending').count()
            
            return {
                'success': True,
                'stats': {
                    'total_partners': total,
                    'verified_partners': verified,
                    'active_partners': active,
                    'pending_verification': pending,
                    'verified_percentage': round((verified / total * 100) if total > 0 else 0, 2)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка получения статистики: {str(e)}'
            }
