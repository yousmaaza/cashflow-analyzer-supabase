-- Create workflow state enum
create type workflow_state as enum (
    'pending',
    'document_processing',
    'transaction_analysis',
    'storage',
    'completed',
    'failed'
);

-- Create transaction category enum
create type transaction_category as enum (
    'income',
    'expense',
    'transfer'
);