-- Create transactions table
create table transactions (
    id uuid primary key default uuid_generate_v4(),
    user_id text not null,
    workflow_id uuid references workflows(id),
    date date not null,
    description text not null,
    amount numeric(15,2) not null,
    category transaction_category,
    metadata jsonb default '{}'::jsonb,
    confidence float default 0.0,
    created_at timestamp with time zone default timezone('utc'::text, now()),
    updated_at timestamp with time zone default timezone('utc'::text, now())
);

-- Create indexes
create index idx_transactions_user_id on transactions(user_id);
create index idx_transactions_workflow_id on transactions(workflow_id);
create index idx_transactions_date on transactions(date);
create index idx_transactions_category on transactions(category);

-- Add trigger for updated_at
create trigger update_transactions_updated_at
    before update on transactions
    for each row
    execute function update_updated_at_column();

-- Add RLS (Row Level Security) policies
alter table transactions enable row level security;

-- Policy: users can only see their own transactions
create policy "Users can view own transactions"
    on transactions for select
    using (auth.uid()::text = user_id);

-- Policy: service role can manage all transactions
create policy "Service can manage all transactions"
    on transactions for all
    using (auth.role() = 'service_role');