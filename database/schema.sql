-- Agentic Marketing Intelligence Platform
-- PostgreSQL Schema (DDL)

CREATE TABLE IF NOT EXISTS categories (
    category_id     SERIAL PRIMARY KEY,
    category_name   VARCHAR(100) NOT NULL,
    parent_category_id INTEGER REFERENCES categories(category_id),
    description     TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id   SERIAL PRIMARY KEY,
    supplier_name VARCHAR(200) NOT NULL,
    contact_name  VARCHAR(100),
    email         VARCHAR(150),
    phone         VARCHAR(30),
    country       VARCHAR(80),
    city          VARCHAR(80),
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS products (
    product_id     SERIAL PRIMARY KEY,
    product_name   VARCHAR(200) NOT NULL,
    category_id    INTEGER REFERENCES categories(category_id),
    supplier_id    INTEGER REFERENCES suppliers(supplier_id),
    unit_price     NUMERIC(10,2) NOT NULL,
    cost_price     NUMERIC(10,2),
    stock_quantity INTEGER DEFAULT 0,
    sku            VARCHAR(50) UNIQUE,
    is_active      BOOLEAN DEFAULT TRUE,
    created_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id       SERIAL PRIMARY KEY,
    first_name        VARCHAR(80) NOT NULL,
    last_name         VARCHAR(80) NOT NULL,
    email             VARCHAR(150) UNIQUE NOT NULL,
    phone             VARCHAR(30),
    date_of_birth     DATE,
    gender            VARCHAR(10),
    country           VARCHAR(80),
    city              VARCHAR(80),
    registration_date TIMESTAMPTZ DEFAULT NOW(),
    is_active         BOOLEAN DEFAULT TRUE,
    customer_segment  VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id   SERIAL PRIMARY KEY,
    customer_id      INTEGER NOT NULL REFERENCES customers(customer_id),
    transaction_date TIMESTAMPTZ NOT NULL,
    total_amount     NUMERIC(12,2) NOT NULL,
    discount_amount  NUMERIC(10,2) DEFAULT 0,
    tax_amount       NUMERIC(10,2) DEFAULT 0,
    payment_method   VARCHAR(50),
    status           VARCHAR(30) DEFAULT 'completed',
    channel          VARCHAR(50),
    created_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id  SERIAL PRIMARY KEY,
    transaction_id INTEGER NOT NULL REFERENCES transactions(transaction_id),
    product_id     INTEGER NOT NULL REFERENCES products(product_id),
    quantity       INTEGER NOT NULL,
    unit_price     NUMERIC(10,2) NOT NULL,
    discount       NUMERIC(10,2) DEFAULT 0
);

CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id     SERIAL PRIMARY KEY,
    campaign_name   VARCHAR(200) NOT NULL,
    campaign_type   VARCHAR(50),
    channel         VARCHAR(50),
    start_date      DATE,
    end_date        DATE,
    budget          NUMERIC(14,2),
    target_segment  VARCHAR(100),
    status          VARCHAR(30) DEFAULT 'active',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS campaign_responses (
    response_id      SERIAL PRIMARY KEY,
    campaign_id      INTEGER NOT NULL REFERENCES campaigns(campaign_id),
    customer_id      INTEGER NOT NULL REFERENCES customers(customer_id),
    response_type    VARCHAR(50),
    response_date    TIMESTAMPTZ,
    converted        BOOLEAN DEFAULT FALSE,
    revenue_generated NUMERIC(10,2) DEFAULT 0
);

CREATE TABLE IF NOT EXISTS website_sessions (
    session_id       SERIAL PRIMARY KEY,
    customer_id      INTEGER REFERENCES customers(customer_id),
    session_date     TIMESTAMPTZ NOT NULL,
    duration_seconds INTEGER,
    pages_visited    INTEGER,
    source           VARCHAR(80),
    device_type      VARCHAR(30),
    bounce           BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS customer_behavior (
    behavior_id      SERIAL PRIMARY KEY,
    customer_id      INTEGER NOT NULL REFERENCES customers(customer_id),
    behavior_date    TIMESTAMPTZ NOT NULL,
    behavior_type    VARCHAR(80),
    product_id       INTEGER REFERENCES products(product_id),
    session_duration INTEGER,
    pages_viewed     INTEGER,
    cart_value       NUMERIC(10,2)
);

-- Generated tables
CREATE TABLE IF NOT EXISTS rfm_scores (
    rfm_id          SERIAL PRIMARY KEY,
    customer_id     INTEGER UNIQUE REFERENCES customers(customer_id),
    recency_days    INTEGER,
    frequency       INTEGER,
    monetary        NUMERIC(14,2),
    recency_score   INTEGER,
    frequency_score INTEGER,
    monetary_score  INTEGER,
    rfm_score       INTEGER,
    rfm_segment     VARCHAR(50),
    calculated_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS customer_segments (
    segment_id      SERIAL PRIMARY KEY,
    customer_id     INTEGER UNIQUE REFERENCES customers(customer_id),
    segment_label   VARCHAR(80),
    segment_cluster INTEGER,
    confidence_score FLOAT,
    features_used   JSONB,
    segmented_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS churn_predictions (
    prediction_id       SERIAL PRIMARY KEY,
    customer_id         INTEGER UNIQUE REFERENCES customers(customer_id),
    churn_probability   FLOAT,
    churn_label         BOOLEAN,
    model_name          VARCHAR(80),
    model_version       VARCHAR(20),
    feature_importances JSONB,
    predicted_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS clv_predictions (
    clv_id        SERIAL PRIMARY KEY,
    customer_id   INTEGER UNIQUE REFERENCES customers(customer_id),
    clv_12m       NUMERIC(14,2),
    clv_24m       NUMERIC(14,2),
    clv_lifetime  NUMERIC(14,2),
    model_name    VARCHAR(80),
    model_version VARCHAR(20),
    predicted_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS model_results (
    result_id        SERIAL PRIMARY KEY,
    model_name       VARCHAR(80) NOT NULL,
    model_version    VARCHAR(20),
    task             VARCHAR(50),
    accuracy         FLOAT,
    precision        FLOAT,
    recall           FLOAT,
    f1_score         FLOAT,
    roc_auc          FLOAT,
    rmse             FLOAT,
    mae              FLOAT,
    r2               FLOAT,
    hyperparameters  JSONB,
    training_samples INTEGER,
    trained_at       TIMESTAMPTZ DEFAULT NOW(),
    is_champion      BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS recommendations (
    recommendation_id SERIAL PRIMARY KEY,
    customer_id       INTEGER REFERENCES customers(customer_id),
    recommendation_type VARCHAR(80),
    title             VARCHAR(200),
    description       TEXT,
    priority          INTEGER DEFAULT 3,
    expected_impact   VARCHAR(200),
    actions           JSONB,
    generated_at      TIMESTAMPTZ DEFAULT NOW(),
    is_applied        BOOLEAN DEFAULT FALSE
);
