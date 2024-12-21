-- Create tables
create table documents (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references auth.users,
  filename text,
  status text,
  created_at timestamp with time zone default timezone('utc'::text, now())
);

create table transactions (
  id uuid default uuid_generate_v4() primary key,
  document_id uuid references documents,
  date date,
  description text,
  amount decimal,
  type text,
  category text,
  created_at timestamp with time zone default timezone('utc'::text, now())
);