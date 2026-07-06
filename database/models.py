from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Date, Text,
    ForeignKey, JSON, Numeric, BigInteger, Index
)
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime


class Base(DeclarativeBase):
    pass


# ─── SOURCE TABLES ───────────────────────────────────────────────────────────

class Category(Base):
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True)
    category_name = Column(String(100), nullable=False)
    parent_category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    products = relationship("Product", back_populates="category")


class Supplier(Base):
    __tablename__ = "suppliers"
    supplier_id = Column(Integer, primary_key=True)
    supplier_name = Column(String(200), nullable=False)
    contact_name = Column(String(100))
    email = Column(String(150))
    phone = Column(String(30))
    country = Column(String(80))
    city = Column(String(80))
    created_at = Column(DateTime, default=datetime.utcnow)
    products = relationship("Product", back_populates="supplier")


class Product(Base):
    __tablename__ = "products"
    product_id = Column(Integer, primary_key=True)
    product_name = Column(String(200), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"))
    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"))
    unit_price = Column(Numeric(10, 2), nullable=False)
    cost_price = Column(Numeric(10, 2))
    stock_quantity = Column(Integer, default=0)
    sku = Column(String(50), unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    category = relationship("Category", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")


class Customer(Base):
    __tablename__ = "customers"
    customer_id = Column(Integer, primary_key=True)
    first_name = Column(String(80), nullable=False)
    last_name = Column(String(80), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    phone = Column(String(30))
    date_of_birth = Column(Date)
    gender = Column(String(10))
    country = Column(String(80))
    city = Column(String(80))
    registration_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    customer_segment = Column(String(50))
    transactions = relationship("Transaction", back_populates="customer")
    rfm_score = relationship("RFMScore", back_populates="customer", uselist=False)
    segment = relationship("CustomerSegment", back_populates="customer", uselist=False)
    churn_prediction = relationship("ChurnPrediction", back_populates="customer", uselist=False)
    clv_prediction = relationship("CLVPrediction", back_populates="customer", uselist=False)


class Transaction(Base):
    __tablename__ = "transactions"
    transaction_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    transaction_date = Column(DateTime, nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    payment_method = Column(String(50))
    status = Column(String(30), default="completed")
    channel = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    customer = relationship("Customer", back_populates="transactions")
    order_items = relationship("OrderItem", back_populates="transaction")
    __table_args__ = (Index("ix_transactions_customer_id", "customer_id"),
                      Index("ix_transactions_date", "transaction_date"),)


class OrderItem(Base):
    __tablename__ = "order_items"
    order_item_id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey("transactions.transaction_id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    discount = Column(Numeric(10, 2), default=0)
    transaction = relationship("Transaction", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")


class Campaign(Base):
    __tablename__ = "campaigns"
    campaign_id = Column(Integer, primary_key=True)
    campaign_name = Column(String(200), nullable=False)
    campaign_type = Column(String(50))
    channel = Column(String(50))
    start_date = Column(Date)
    end_date = Column(Date)
    budget = Column(Numeric(14, 2))
    target_segment = Column(String(100))
    status = Column(String(30), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    responses = relationship("CampaignResponse", back_populates="campaign")


class CampaignResponse(Base):
    __tablename__ = "campaign_responses"
    response_id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.campaign_id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    response_type = Column(String(50))
    response_date = Column(DateTime)
    converted = Column(Boolean, default=False)
    revenue_generated = Column(Numeric(10, 2), default=0)
    campaign = relationship("Campaign", back_populates="responses")


class WebsiteSession(Base):
    __tablename__ = "website_sessions"
    session_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=True)
    session_date = Column(DateTime, nullable=False)
    duration_seconds = Column(Integer)
    pages_visited = Column(Integer)
    source = Column(String(80))
    device_type = Column(String(30))
    bounce = Column(Boolean, default=False)


class CustomerBehavior(Base):
    __tablename__ = "customer_behavior"
    behavior_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    behavior_date = Column(DateTime, nullable=False)
    behavior_type = Column(String(80))
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=True)
    session_duration = Column(Integer)
    pages_viewed = Column(Integer)
    cart_value = Column(Numeric(10, 2))


# ─── GENERATED TABLES ────────────────────────────────────────────────────────

class RFMScore(Base):
    __tablename__ = "rfm_scores"
    rfm_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), unique=True)
    recency_days = Column(Integer)
    frequency = Column(Integer)
    monetary = Column(Numeric(14, 2))
    recency_score = Column(Integer)
    frequency_score = Column(Integer)
    monetary_score = Column(Integer)
    rfm_score = Column(Integer)
    rfm_segment = Column(String(50))
    calculated_at = Column(DateTime, default=datetime.utcnow)
    customer = relationship("Customer", back_populates="rfm_score")


class CustomerSegment(Base):
    __tablename__ = "customer_segments"
    segment_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), unique=True)
    segment_label = Column(String(80))
    segment_cluster = Column(Integer)
    confidence_score = Column(Float)
    features_used = Column(JSON)
    segmented_at = Column(DateTime, default=datetime.utcnow)
    customer = relationship("Customer", back_populates="segment")


class ChurnPrediction(Base):
    __tablename__ = "churn_predictions"
    prediction_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), unique=True)
    churn_probability = Column(Float)
    churn_label = Column(Boolean)
    model_name = Column(String(80))
    model_version = Column(String(20))
    feature_importances = Column(JSON)
    predicted_at = Column(DateTime, default=datetime.utcnow)
    customer = relationship("Customer", back_populates="churn_prediction")


class CLVPrediction(Base):
    __tablename__ = "clv_predictions"
    clv_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), unique=True)
    clv_12m = Column(Numeric(14, 2))
    clv_24m = Column(Numeric(14, 2))
    clv_lifetime = Column(Numeric(14, 2))
    model_name = Column(String(80))
    model_version = Column(String(20))
    predicted_at = Column(DateTime, default=datetime.utcnow)
    customer = relationship("Customer", back_populates="clv_prediction")


class ModelResult(Base):
    __tablename__ = "model_results"
    result_id = Column(Integer, primary_key=True)
    model_name = Column(String(80), nullable=False)
    model_version = Column(String(20))
    task = Column(String(50))
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    roc_auc = Column(Float)
    rmse = Column(Float)
    mae = Column(Float)
    r2 = Column(Float)
    hyperparameters = Column(JSON)
    training_samples = Column(Integer)
    trained_at = Column(DateTime, default=datetime.utcnow)
    is_champion = Column(Boolean, default=False)


class Recommendation(Base):
    __tablename__ = "recommendations"
    recommendation_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=True)
    recommendation_type = Column(String(80))
    title = Column(String(200))
    description = Column(Text)
    priority = Column(Integer, default=3)
    expected_impact = Column(String(200))
    actions = Column(JSON)
    generated_at = Column(DateTime, default=datetime.utcnow)
    is_applied = Column(Boolean, default=False)
