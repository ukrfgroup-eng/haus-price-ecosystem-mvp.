"""
API ДЛЯ РАБОТЫ С ПАРТНЕРАМИ
Согласно ТЗ: API ДЛЯ РАБОТЫ С ПАРТНЕРАМИ
"""

from flask import Blueprint, request, jsonify, current_app
from sqlalchemy.exc import IntegrityError
from .models import db, Partner, PartnerVerificationLog
from .verification_service import VerificationService

partner_bp = Blueprint('partners', __name__, url_prefix='/api/v1/partners')
verification_service = VerificationService()

@partner_bp.route('/register', methods=['POST'])
def register_partner():
    """Регистрация нового партнера"""
    try:
        data = request.get_json()
        
        # Валидация обязательных полей
        required_fields = ['company_name', 'legal_form', 'inn', 'contact_person', 'phone', 'email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Не заполнено обязательное поле: {field}'
                }), 400
        
        # Проверка ИНН через API ФНС
        inn_verification = verification_service.verify_inn(data['inn'])
        if not inn_verification['success']:
            return jsonify({
                'success': False,
                'error': 'Ошибка верификации ИНН',
                'details': inn_verification.get('error')
            }), 400
        
        # Генерация кода партнера
        from datetime import datetime
        import random
        date_str = datetime.now().strftime('%y%m%d')
        random_str = ''.join(random.choices('0123456789', k=4))
        partner_code = f"P-{date_str}-{random_str}"
        
        # Создание партнера
        partner = Partner(
            partner_code=partner_code,
            company_name=data['company_name'],
            legal_form=data['legal_form'],
            inn=data['inn'],
            contact_person=data['contact_person'],
            phone=data['phone'],
            email=data['email'],
            verification_data=inn_verification.get('data'),
            verification_status='pending_documents' if inn_verification['success'] else 'rejected',
            status='registration_in_progress',
            registration_stage='inn_verified'
        )
        
        # Опциональные поля
        if data.get('ogrn'):
            partner.ogrn = data['ogrn']
        if data.get('legal_address'):
            partner.legal_address = data['legal_address']
        if data.get('website'):
            partner.website = data['website']
        
        db.session.add(partner)
        
        # Логирование верификации
        log = PartnerVerificationLog(
            partner_id=partner.id,
            partner_code=partner_code,
            action='inn_check',
            status='success' if inn_verification['success'] else 'failed',
            details=inn_verification,
            performed_by='system'
        )
        db.session.add(log)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'partner': partner.to_dict(),
            'message': 'Регистрация начата успешно',
            'next_steps': [
                {
                    'step': 'upload_documents',
                    'description': 'Загрузите документы компании',
                    'url': f"/partner/upload/{partner_code}"
                },
                {
                    'step': 'complete_profile',
                    'description': 'Заполните профиль услуг и специализаций',
                    'url': f"/partner/profile/{partner_code}"
                }
            ]
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Компания с таким ИНН уже зарегистрирована'
        }), 409
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Ошибка регистрации партнера: {e}")
        return jsonify({
            'success': False,
            'error': 'Внутренняя ошибка сервера'
        }), 500

@partner_bp.route('/search', methods=['POST'])
def search_partners():
    """Поиск партнеров по критериям"""
    try:
        criteria = request.get_json()
        
        # Базовый запрос только верифицированных и активных партнеров
        query = Partner.query.filter(
            Partner.verification_status == 'verified',
            Partner.is_active == True
        )
        
        # Фильтр по региону
        if criteria.get('region'):
            query = query.filter(Partner.regions.contains([criteria['region']]))
        
        # Фильтр по специализациям
        if criteria.get('specializations'):
            query = query.filter(
                Partner.specializations.overlap(criteria['specializations'])
            )
        
        # Фильтр по категории
        if criteria.get('main_category'):
            query = query.filter(Partner.main_category == criteria['main_category'])
        
        # Сортировка по рейтингу
        query = query.order_by(Partner.rating.desc(), Partner.created_at.desc())
        
        # Пагинация
        page = criteria.get('page', 1)
        per_page = min(criteria.get('per_page', 10), 50)
        partners = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'partners': [p.to_dict() for p in partners.items],
            'pagination': {
                'page': partners.page,
                'per_page': partners.per_page,
                'total': partners.total,
                'pages': partners.pages
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Ошибка поиска партнеров: {e}")
        return jsonify({
            'success': False,
            'error': 'Ошибка при поиске партнеров'
        }), 500

@partner_bp.route('/<partner_code>', methods=['GET'])
def get_partner(partner_code):
    """Получение информации о партнере"""
    partner = Partner.query.filter_by(partner_code=partner_code).first()
    
    if not partner:
        return jsonify({'success': False, 'error': 'Партнер не найден'}), 404
    
    return jsonify({'success': True, 'partner': partner.to_dict()})

@partner_bp.route('/<partner_code>/profile', methods=['PUT'])
def update_partner_profile(partner_code):
    """Обновление профиля партнера"""
    try:
        partner = Partner.query.filter_by(partner_code=partner_code).first()
        if not partner:
            return jsonify({'success': False, 'error': 'Партнер не найден'}), 404
        
        data = request.get_json()
        
        # Обновление полей профиля
        update_fields = ['main_category', 'specializations', 'services', 'regions', 'cities']
        for field in update_fields:
            if field in data:
                setattr(partner, field, data[field])
        
        partner.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Профиль успешно обновлен',
            'partner': partner.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Ошибка обновления профиля: {e}")
        return jsonify({'success': False, 'error': 'Ошибка обновления'}), 500
