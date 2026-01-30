-- Миграция 001: Создание основных таблиц для блока партнеров
-- Выполняется при первом запуске системы

-- Таблица партнеров (основная)
CREATE TABLE IF NOT EXISTS partners (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Юридическая информация
    company_name VARCHAR(200) NOT NULL,
    trading_name VARCHAR(200),
    legal_form VARCHAR(10) NOT NULL CHECK (legal_form IN ('ООО', 'ИП', 'АО', 'ЗАО', 'Не определено')),
    inn VARCHAR(12) UNIQUE NOT NULL,
    ogrn VARCHAR(15),
    kpp VARCHAR(9),
    legal_address TEXT NOT NULL,
    actual_address TEXT,
    
    -- Контактная информация
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(120) NOT NULL,
    website VARCHAR(200),
    contact_person VARCHAR(100) NOT NULL,
    contact_position VARCHAR(100),
    telegram VARCHAR(100),
    whatsapp VARCHAR(20),
    
    -- Профиль услуг (храним как JSON)
    main_category VARCHAR(100),
    specializations JSONB DEFAULT '[]',
    services JSONB DEFAULT '[]',
    portfolio JSONB DEFAULT '[]',
    
    -- География работы
    regions JSONB DEFAULT '[]',
    cities JSONB DEFAULT '[]',
    work_radius_km INTEGER,
    
    -- Верификация
    verification_status VARCHAR(20) DEFAULT 'pending' 
        CHECK (verification_status IN ('pending', 'in_progress', 'verified', 'rejected', 'suspended')),
    verification_score FLOAT DEFAULT 0.0,
    verification_date TIMESTAMP,
    verified_by VARCHAR(50),
    rejection_reason TEXT,
    
    -- Документы (ссылки на хранилище)
    documents JSONB DEFAULT '[]',
    
    -- Настройки и статус
    tier VARCHAR(20) DEFAULT 'basic' CHECK (tier IN ('basic', 'pro', 'enterprise')),
    is_active BOOLEAN DEFAULT TRUE,
    is_blocked BOOLEAN DEFAULT FALSE,
    max_active_leads INTEGER DEFAULT 3,
    subscription_expires TIMESTAMP,
    
    -- Рейтинг и статистика
    rating FLOAT DEFAULT 0.0,
    reviews_count INTEGER DEFAULT 0,
    completed_projects INTEGER DEFAULT 0,
    response_time_avg FLOAT,
    
    -- Технические поля
    public_id VARCHAR(50) UNIQUE NOT NULL,
    created_by VARCHAR(50),
    metadata JSONB DEFAULT '{}',
    
    -- Временные метки
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Индексы для ускорения поиска
    INDEX idx_partners_verification_status (verification_status),
    INDEX idx_partners_is_active (is_active),
    INDEX idx_partners_rating (rating),
    INDEX idx_partners_created_at (created_at),
    INDEX idx_partners_regions (regions) USING GIN,
    INDEX idx_partners_cities (cities) USING GIN,
    INDEX idx_partners_specializations (specializations) USING GIN
);

-- Таблица логов верификации
CREATE TABLE IF NOT EXISTS verification_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    partner_id UUID NOT NULL REFERENCES partners(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    details JSONB DEFAULT '{}',
    performed_by VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_verification_logs_partner_id (partner_id),
    INDEX idx_verification_logs_created_at (created_at)
);

-- Таблица статистики партнеров
CREATE TABLE IF NOT EXISTS partner_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    partner_id UUID NOT NULL UNIQUE REFERENCES partners(id) ON DELETE CASCADE,
    total_leads INTEGER DEFAULT 0,
    accepted_leads INTEGER DEFAULT 0,
    rejected_leads INTEGER DEFAULT 0,
    completed_leads INTEGER DEFAULT 0,
    avg_response_time_hours FLOAT,
    customer_satisfaction FLOAT DEFAULT 0.0,
    last_activity TIMESTAMP,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_partner_stats_partner_id (partner_id)
);

-- Таблица поискового индекса (для быстрого поиска)
CREATE TABLE IF NOT EXISTS search_index (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    partner_id UUID NOT NULL REFERENCES partners(id) ON DELETE CASCADE,
    search_vector TSVECTOR,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_search_index_vector (search_vector) USING GIN
);

-- Триггер для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_partners_updated_at 
    BEFORE UPDATE ON partners 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Триггер для генерации публичного ID
CREATE OR REPLACE FUNCTION generate_public_id()
RETURNS TRIGGER AS $$
DECLARE
    prefix TEXT := 'PART';
    random_num INTEGER;
    new_public_id TEXT;
BEGIN
    -- Генерируем 6-значное число
    random_num := floor(random() * 900000 + 100000);
    new_public_id := prefix || '-' || random_num;
    
    -- Проверяем уникальность
    WHILE EXISTS (SELECT 1 FROM partners WHERE public_id = new_public_id) LOOP
        random_num := floor(random() * 900000 + 100000);
        new_public_id := prefix || '-' || random_num;
    END LOOP;
    
    NEW.public_id := new_public_id;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER set_partner_public_id 
    BEFORE INSERT ON partners 
    FOR EACH ROW EXECUTE FUNCTION generate_public_id();

-- Функция для обновления поискового вектора
CREATE OR REPLACE FUNCTION update_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO search_index (partner_id, search_vector, last_updated)
    VALUES (
        NEW.id,
        to_tsvector('russian', 
            COALESCE(NEW.company_name, '') || ' ' ||
            COALESCE(NEW.trading_name, '') || ' ' ||
            COALESCE(NEW.main_category, '') || ' ' ||
            COALESCE(array_to_string(NEW.specializations, ' '), '')
        ),
        CURRENT_TIMESTAMP
    )
    ON CONFLICT (partner_id) 
    DO UPDATE SET 
        search_vector = EXCLUDED.search_vector,
        last_updated = EXCLUDED.last_updated;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_partner_search_vector 
    AFTER INSERT OR UPDATE ON partners 
    FOR EACH ROW EXECUTE FUNCTION update_search_vector();

-- Комментарии к таблицам
COMMENT ON TABLE partners IS 'Основная таблица партнеров';
COMMENT ON TABLE verification_logs IS 'Логи верификации партнеров';
COMMENT ON TABLE partner_stats IS 'Статистика по партнерам';
COMMENT ON TABLE search_index IS 'Поисковый индекс для быстрого поиска партнеров';
