"""Initial schema migration.

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create domains table
    op.create_table('domains',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('key', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('risk_profile', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )
    op.create_index(op.f('ix_domains_key'), 'domains', ['key'], unique=False)

    # Create jurisdictions table
    op.create_table('jurisdictions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('region', sa.String(length=50), nullable=True),
        sa.Column('regulatory_environment', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_jurisdictions_code'), 'jurisdictions', ['code'], unique=False)

    # Create policies table
    op.create_table('policies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('body_text', sa.Text(), nullable=False),
        sa.Column('jurisdiction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('policy_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('effective_date', sa.DateTime(), nullable=True),
        sa.Column('source_url', sa.String(length=500), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['jurisdiction_id'], ['jurisdictions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_policy_jurisdiction_type', 'policies', ['jurisdiction_id', 'policy_type'], unique=False)
    op.create_index('idx_policy_effective_date', 'policies', ['effective_date'], unique=False)

    # Create debate_documents table
    op.create_table('debate_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('session_date', sa.DateTime(), nullable=True),
        sa.Column('jurisdiction_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('policy_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('document_type', sa.String(length=50), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['jurisdiction_id'], ['jurisdictions.id'], ),
        sa.ForeignKeyConstraint(['policy_id'], ['policies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_debate_doc_policy', 'debate_documents', ['policy_id'], unique=False)
    op.create_index('idx_debate_doc_session_date', 'debate_documents', ['session_date'], unique=False)

    # Create debate_segments table
    op.create_table('debate_segments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('segment_text', sa.Text(), nullable=False),
        sa.Column('speaker', sa.String(length=100), nullable=True),
        sa.Column('segment_type', sa.String(length=50), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=True),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['debate_documents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_segment_document', 'debate_segments', ['document_id'], unique=False)
    op.create_index('idx_segment_speaker', 'debate_segments', ['speaker'], unique=False)

    # Create arguments table
    op.create_table('arguments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('segment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('claim_text', sa.Text(), nullable=False),
        sa.Column('evidence_text', sa.Text(), nullable=True),
        sa.Column('claim_type', sa.String(length=50), nullable=True),
        sa.Column('stance_label', sa.String(length=20), nullable=True),
        sa.Column('stance_target', sa.String(length=100), nullable=True),
        sa.Column('argument_role', sa.String(length=50), nullable=True),
        sa.Column('frame_label', sa.String(length=100), nullable=True),
        sa.Column('salience_score', sa.Float(), nullable=True),
        sa.Column('credibility_score', sa.Float(), nullable=True),
        sa.Column('uncertainty_score', sa.Float(), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['segment_id'], ['debate_segments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_argument_segment', 'arguments', ['segment_id'], unique=False)
    op.create_index('idx_argument_stance', 'arguments', ['stance_label'], unique=False)
    op.create_index('idx_argument_role', 'arguments', ['argument_role'], unique=False)
    op.create_index('idx_argument_salience', 'arguments', ['salience_score'], unique=False)

    # Create argument_edges table
    op.create_table('argument_edges',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('from_argument_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('to_argument_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('relation_type', sa.String(length=50), nullable=False),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['from_argument_id'], ['arguments.id'], ),
        sa.ForeignKeyConstraint(['to_argument_id'], ['arguments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_edge_from_argument', 'argument_edges', ['from_argument_id'], unique=False)
    op.create_index('idx_edge_to_argument', 'argument_edges', ['to_argument_id'], unique=False)
    op.create_index('idx_edge_relation', 'argument_edges', ['relation_type'], unique=False)

    # Create domain_features table
    op.create_table('domain_features',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('domain_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('feature_name', sa.String(length=100), nullable=False),
        sa.Column('feature_description', sa.Text(), nullable=True),
        sa.Column('feature_type', sa.String(length=50), nullable=True),
        sa.Column('default_value', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('validation_rules', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['domain_id'], ['domains.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_feature_domain', 'domain_features', ['domain_id'], unique=False)
    op.create_index('idx_feature_name', 'domain_features', ['feature_name'], unique=False)

    # Create scenarios table
    op.create_table('scenarios',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('domain_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scenario_type', sa.String(length=50), nullable=True),
        sa.Column('parameters', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['domain_id'], ['domains.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_scenario_domain', 'scenarios', ['domain_id'], unique=False)
    op.create_index('idx_scenario_type', 'scenarios', ['scenario_type'], unique=False)

    # Create scenario_runs table
    op.create_table('scenario_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scenario_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('run_name', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('num_iterations', sa.Integer(), nullable=False),
        sa.Column('time_horizon_days', sa.Integer(), nullable=False),
        sa.Column('seed', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['scenario_id'], ['scenarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_run_scenario', 'scenario_runs', ['scenario_id'], unique=False)
    op.create_index('idx_run_status', 'scenario_runs', ['status'], unique=False)
    op.create_index('idx_run_started_at', 'scenario_runs', ['started_at'], unique=False)

    # Create scenario_results table
    op.create_table('scenario_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('run_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('iteration', sa.Integer(), nullable=False),
        sa.Column('shocks', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('features', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('outcomes', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['run_id'], ['scenario_runs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_result_run', 'scenario_results', ['run_id'], unique=False)
    op.create_index('idx_result_iteration', 'scenario_results', ['iteration'], unique=False)

    # Create funds table
    op.create_table('funds',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('fund_type', sa.String(length=50), nullable=True),
        sa.Column('size_usd', sa.Float(), nullable=True),
        sa.Column('vintage_year', sa.Integer(), nullable=True),
        sa.Column('focus_areas', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('jurisdictions', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_fund_type', 'funds', ['fund_type'], unique=False)
    op.create_index('idx_fund_vintage', 'funds', ['vintage_year'], unique=False)

    # Create portfolios table
    op.create_table('portfolios',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('fund_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('domain_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('base_currency', sa.String(length=3), nullable=True),
        sa.Column('total_value_usd', sa.Float(), nullable=True),
        sa.Column('risk_profile', sa.String(length=20), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['domain_id'], ['domains.id'], ),
        sa.ForeignKeyConstraint(['fund_id'], ['funds.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_portfolio_fund', 'portfolios', ['fund_id'], unique=False)
    op.create_index('idx_portfolio_domain', 'portfolios', ['domain_id'], unique=False)
    op.create_index('idx_portfolio_risk', 'portfolios', ['risk_profile'], unique=False)

    # Create startups table
    op.create_table('startups',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('domain_key', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('founded_date', sa.DateTime(), nullable=True),
        sa.Column('stage', sa.String(length=50), nullable=True),
        sa.Column('valuation_usd', sa.Float(), nullable=True),
        sa.Column('revenue_usd', sa.Float(), nullable=True),
        sa.Column('employee_count', sa.Integer(), nullable=True),
        sa.Column('headquarters', sa.String(length=100), nullable=True),
        sa.Column('jurisdictions', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('features', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_startup_domain', 'startups', ['domain_key'], unique=False)
    op.create_index('idx_startup_stage', 'startups', ['stage'], unique=False)
    op.create_index('idx_startup_valuation', 'startups', ['valuation_usd'], unique=False)

    # Create holdings table
    op.create_table('holdings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('portfolio_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('startup_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('weight', sa.Float(), nullable=False),
        sa.Column('investment_amount_usd', sa.Float(), nullable=True),
        sa.Column('investment_date', sa.DateTime(), nullable=True),
        sa.Column('exit_date', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ),
        sa.ForeignKeyConstraint(['startup_id'], ['startups.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_holding_portfolio', 'holdings', ['portfolio_id'], unique=False)
    op.create_index('idx_holding_startup', 'holdings', ['startup_id'], unique=False)
    op.create_index('idx_holding_status', 'holdings', ['status'], unique=False)

    # Create legacy tables for backward compatibility
    op.create_table('articles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('published_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('sentiment_analysis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('article_id', sa.Integer(), nullable=False),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('sentiment_label', sa.String(length=20), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('topic_modeling',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('article_id', sa.Integer(), nullable=False),
        sa.Column('topics', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('dominant_topic', sa.String(length=100), nullable=True),
        sa.Column('topic_confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('topic_modeling')
    op.drop_table('sentiment_analysis')
    op.drop_table('articles')
    op.drop_table('holdings')
    op.drop_table('startups')
    op.drop_table('portfolios')
    op.drop_table('funds')
    op.drop_table('scenario_results')
    op.drop_table('scenario_runs')
    op.drop_table('scenarios')
    op.drop_table('domain_features')
    op.drop_table('argument_edges')
    op.drop_table('arguments')
    op.drop_table('debate_segments')
    op.drop_table('debate_documents')
    op.drop_table('policies')
    op.drop_table('jurisdictions')
    op.drop_table('domains')








