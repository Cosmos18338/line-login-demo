CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 用戶主表
CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_name   VARCHAR(100),
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 第三方登入綁定表
CREATE TABLE user_oauth_bindings (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider            VARCHAR(20) NOT NULL,
    provider_user_id    VARCHAR(100) NOT NULL,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT uq_provider_user UNIQUE (provider, provider_user_id),
    CONSTRAINT uq_user_provider UNIQUE (user_id, provider)
);

-- 系統代碼字典表 (CODD表)
CREATE TABLE codes (
    id              BIGSERIAL PRIMARY KEY,
    category_code   VARCHAR(20) NOT NULL,
    code_id         VARCHAR(20) NOT NULL,
    code_name       VARCHAR(100) NOT NULL,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT uq_category_code UNIQUE (category_code, code_id)
);

