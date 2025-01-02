-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- Create enum for workflow states
create type workflow_state as enum (
    'pending',
    'document_processing',
    'transaction_analysis',
    'storage',
    'completed',
    'failed'
);

-- Create workflows table
create table workflows (
    id uuid primary key default uuid_generate_v4(),
    user_id text not null,
    document_path text not null,
    state workflow_state not null default 'pending',
    created_at timestamp with time zone default timezone('utc'::text, now()),
    updated_at timestamp with time zone default timezone('utc'::text, now()),
    error text,
    results jsonb default '{}'::jsonb,
    retries integer default 0,
    last_retry_at timestamp with time zone
);

-- Create index on user_id for faster lookups
create index idx_workflows_user_id on workflows(user_id);

-- Create index on state for status queries
create index idx_workflows_state on workflows(state);

-- Add trigger for updating updated_at timestamp
create or replace function update_updated_at_column()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

create trigger update_workflows_updated_at
    before update on workflows
    for each row
    execute function update_updated_at_column();