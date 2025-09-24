"""
Database Models Module.

This module defines SQLAlchemy models for the startup performance
prediction system.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime
import uuid

Base = declarative_base()


class Domain(Base):
    """Domain model for different startup domains."""
    __tablename__ = 'domains'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(50))
    risk_profile = Column(String(20))  # low, medium, high
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    features = relationship("DomainFeature", back_populates="domain")
    scenarios = relationship("Scenario", back_populates="domain")
    portfolios = relationship("Portfolio", back_populates="domain")


class Jurisdiction(Base):
    """Jurisdiction model for different regulatory jurisdictions."""
    __tablename__ = 'jurisdictions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    region = Column(String(50))
    regulatory_environment = Column(String(20))  # strict, moderate, lenient
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    policies = relationship("Policy", back_populates="jurisdiction")


class Policy(Base):
    """Policy model for regulatory policies and documents."""
    __tablename__ = 'policies'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    body_text = Column(Text, nullable=False)
    jurisdiction_id = Column(UUID(as_uuid=True), ForeignKey('jurisdictions.id'), nullable=False)
    policy_type = Column(String(50), nullable=False)  # regulation, guidance, legislation, etc.
    status = Column(String(20), default='active')  # active, draft, repealed
    effective_date = Column(DateTime)
    source_url = Column(String(500))
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    jurisdiction = relationship("Jurisdiction", back_populates="policies")
    debate_documents = relationship("DebateDocument", back_populates="policy")
    
    # Indexes
    __table_args__ = (
        Index('idx_policy_jurisdiction_type', 'jurisdiction_id', 'policy_type'),
        Index('idx_policy_effective_date', 'effective_date'),
    )


class DebateDocument(Base):
    """Debate document model for policy discussions and transcripts."""
    __tablename__ = 'debate_documents'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    source = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    session_date = Column(DateTime)
    jurisdiction_id = Column(UUID(as_uuid=True), ForeignKey('jurisdictions.id'))
    policy_id = Column(UUID(as_uuid=True), ForeignKey('policies.id'))
    document_type = Column(String(50))  # transcript, press_release, statement
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    jurisdiction = relationship("Jurisdiction")
    policy = relationship("Policy", back_populates="debate_documents")
    segments = relationship("DebateSegment", back_populates="document")
    
    # Indexes
    __table_args__ = (
        Index('idx_debate_doc_policy', 'policy_id'),
        Index('idx_debate_doc_session_date', 'session_date'),
    )


class DebateSegment(Base):
    """Debate segment model for individual segments of debate documents."""
    __tablename__ = 'debate_segments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('debate_documents.id'), nullable=False)
    segment_text = Column(Text, nullable=False)
    speaker = Column(String(100))
    segment_type = Column(String(50))  # statement, question, response
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("DebateDocument", back_populates="segments")
    arguments = relationship("Argument", back_populates="segment")
    
    # Indexes
    __table_args__ = (
        Index('idx_segment_document', 'document_id'),
        Index('idx_segment_speaker', 'speaker'),
    )


class Argument(Base):
    """Argument model for extracted arguments from debate segments."""
    __tablename__ = 'arguments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    segment_id = Column(UUID(as_uuid=True), ForeignKey('debate_segments.id'), nullable=False)
    claim_text = Column(Text, nullable=False)
    evidence_text = Column(Text)
    claim_type = Column(String(50))  # causal, normative, factual
    stance_label = Column(String(20))  # support, oppose, neutral
    stance_target = Column(String(100))
    argument_role = Column(String(50))  # claim, premise, attack, support, rebut
    frame_label = Column(String(100))
    salience_score = Column(Float)
    credibility_score = Column(Float)
    uncertainty_score = Column(Float)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    segment = relationship("DebateSegment", back_populates="arguments")
    edges = relationship("ArgumentEdge", foreign_keys="ArgumentEdge.from_argument_id")
    incoming_edges = relationship("ArgumentEdge", foreign_keys="ArgumentEdge.to_argument_id")
    
    # Indexes
    __table_args__ = (
        Index('idx_argument_segment', 'segment_id'),
        Index('idx_argument_stance', 'stance_label'),
        Index('idx_argument_role', 'argument_role'),
        Index('idx_argument_salience', 'salience_score'),
    )


class ArgumentEdge(Base):
    """Argument edge model for relationships between arguments."""
    __tablename__ = 'argument_edges'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_argument_id = Column(UUID(as_uuid=True), ForeignKey('arguments.id'), nullable=False)
    to_argument_id = Column(UUID(as_uuid=True), ForeignKey('arguments.id'), nullable=False)
    relation_type = Column(String(50), nullable=False)  # supports, attacks, rebuts, elaborates
    weight = Column(Float, default=1.0)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    from_argument = relationship("Argument", foreign_keys=[from_argument_id])
    to_argument = relationship("Argument", foreign_keys=[to_argument_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_edge_from_argument', 'from_argument_id'),
        Index('idx_edge_to_argument', 'to_argument_id'),
        Index('idx_edge_relation', 'relation_type'),
    )


class DomainFeature(Base):
    """Domain feature model for domain-specific features."""
    __tablename__ = 'domain_features'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain_id = Column(UUID(as_uuid=True), ForeignKey('domains.id'), nullable=False)
    feature_name = Column(String(100), nullable=False)
    feature_description = Column(Text)
    feature_type = Column(String(50))  # float, int, string, dict
    default_value = Column(JSON)
    validation_rules = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    domain = relationship("Domain", back_populates="features")
    
    # Indexes
    __table_args__ = (
        Index('idx_feature_domain', 'domain_id'),
        Index('idx_feature_name', 'feature_name'),
    )


class Scenario(Base):
    """Scenario model for simulation scenarios."""
    __tablename__ = 'scenarios'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    domain_id = Column(UUID(as_uuid=True), ForeignKey('domains.id'), nullable=False)
    scenario_type = Column(String(50))  # monte_carlo, what_if, stress_test
    parameters = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    domain = relationship("Domain", back_populates="scenarios")
    runs = relationship("ScenarioRun", back_populates="scenario")
    
    # Indexes
    __table_args__ = (
        Index('idx_scenario_domain', 'domain_id'),
        Index('idx_scenario_type', 'scenario_type'),
    )


class ScenarioRun(Base):
    """Scenario run model for individual scenario executions."""
    __tablename__ = 'scenario_runs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scenario_id = Column(UUID(as_uuid=True), ForeignKey('scenarios.id'), nullable=False)
    run_name = Column(String(100))
    status = Column(String(20), default='running')  # running, completed, failed
    num_iterations = Column(Integer, nullable=False)
    time_horizon_days = Column(Integer, nullable=False)
    seed = Column(Integer)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    metadata = Column(JSON)
    
    # Relationships
    scenario = relationship("Scenario", back_populates="runs")
    results = relationship("ScenarioResult", back_populates="run")
    
    # Indexes
    __table_args__ = (
        Index('idx_run_scenario', 'scenario_id'),
        Index('idx_run_status', 'status'),
        Index('idx_run_started_at', 'started_at'),
    )


class ScenarioResult(Base):
    """Scenario result model for simulation outcomes."""
    __tablename__ = 'scenario_results'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), ForeignKey('scenario_runs.id'), nullable=False)
    iteration = Column(Integer, nullable=False)
    shocks = Column(JSON)  # List of shock data
    features = Column(JSON)  # Input features
    outcomes = Column(JSON, nullable=False)  # Simulation outcomes
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    run = relationship("ScenarioRun", back_populates="results")
    
    # Indexes
    __table_args__ = (
        Index('idx_result_run', 'run_id'),
        Index('idx_result_iteration', 'iteration'),
    )


class Fund(Base):
    """Fund model for investment funds."""
    __tablename__ = 'funds'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    fund_type = Column(String(50))  # vc, pe, angel, corporate
    size_usd = Column(Float)
    vintage_year = Column(Integer)
    focus_areas = Column(ARRAY(String))
    jurisdictions = Column(ARRAY(String))
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    portfolios = relationship("Portfolio", back_populates="fund")
    
    # Indexes
    __table_args__ = (
        Index('idx_fund_type', 'fund_type'),
        Index('idx_fund_vintage', 'vintage_year'),
    )


class Portfolio(Base):
    """Portfolio model for investment portfolios."""
    __tablename__ = 'portfolios'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    fund_id = Column(UUID(as_uuid=True), ForeignKey('funds.id'))
    domain_id = Column(UUID(as_uuid=True), ForeignKey('domains.id'))
    base_currency = Column(String(3), default='USD')
    total_value_usd = Column(Float)
    risk_profile = Column(String(20))  # conservative, moderate, aggressive
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    fund = relationship("Fund", back_populates="portfolios")
    domain = relationship("Domain", back_populates="portfolios")
    holdings = relationship("Holding", back_populates="portfolio")
    
    # Indexes
    __table_args__ = (
        Index('idx_portfolio_fund', 'fund_id'),
        Index('idx_portfolio_domain', 'domain_id'),
        Index('idx_portfolio_risk', 'risk_profile'),
    )


class Holding(Base):
    """Holding model for individual portfolio holdings."""
    __tablename__ = 'holdings'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey('portfolios.id'), nullable=False)
    startup_id = Column(UUID(as_uuid=True), ForeignKey('startups.id'), nullable=False)
    weight = Column(Float, nullable=False)  # Portfolio weight (0-1)
    investment_amount_usd = Column(Float)
    investment_date = Column(DateTime)
    exit_date = Column(DateTime)
    status = Column(String(20), default='active')  # active, exited, written_off
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")
    startup = relationship("Startup", back_populates="holdings")
    
    # Indexes
    __table_args__ = (
        Index('idx_holding_portfolio', 'portfolio_id'),
        Index('idx_holding_startup', 'startup_id'),
        Index('idx_holding_status', 'status'),
    )


class Startup(Base):
    """Startup model for individual startups."""
    __tablename__ = 'startups'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    domain_key = Column(String(50), nullable=False)
    description = Column(Text)
    founded_date = Column(DateTime)
    stage = Column(String(50))  # seed, series_a, series_b, etc.
    valuation_usd = Column(Float)
    revenue_usd = Column(Float)
    employee_count = Column(Integer)
    headquarters = Column(String(100))
    jurisdictions = Column(ARRAY(String))
    features = Column(JSON)  # Domain-specific features
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    holdings = relationship("Holding", back_populates="startup")
    
    # Indexes
    __table_args__ = (
        Index('idx_startup_domain', 'domain_key'),
        Index('idx_startup_stage', 'stage'),
        Index('idx_startup_valuation', 'valuation_usd'),
    )


# Legacy models for backward compatibility
class Article(Base):
    """Legacy article model for news articles."""
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String(100))
    url = Column(String(500))
    published_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class SentimentAnalysis(Base):
    """Legacy sentiment analysis model."""
    __tablename__ = 'sentiment_analysis'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('articles.id'), nullable=False)
    sentiment_score = Column(Float)
    sentiment_label = Column(String(20))
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    article = relationship("Article")


class TopicModeling(Base):
    """Legacy topic modeling model."""
    __tablename__ = 'topic_modeling'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('articles.id'), nullable=False)
    topics = Column(JSON)
    dominant_topic = Column(String(100))
    topic_confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    article = relationship("Article")








