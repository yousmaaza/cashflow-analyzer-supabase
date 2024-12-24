# Migrations Supabase

Ce dossier contient les scripts SQL pour initialiser et mettre à jour la structure de la base de données Supabase pour le service d'orchestration.

## 📚 Structure des migrations

```
migrations/
├── 01_create_enums.sql       # Types énumérés
├── 02_create_workflows.sql   # Table workflows
├── 03_create_transactions.sql # Table transactions
└── README.md               # Documentation
```

## 📝 Description des tables

### Table `workflows`
```sql
create table workflows (
    id uuid primary key,
    user_id text not null,
    document_path text not null,
    state workflow_state not null,
    error text,
    results jsonb,
    retries integer,
    last_retry_at timestamptz,
    created_at timestamptz,
    updated_at timestamptz
);
```

### Table `transactions`
```sql
create table transactions (
    id uuid primary key,
    user_id text not null,
    workflow_id uuid references workflows(id),
    date date not null,
    description text not null,
    amount numeric(15,2) not null,
    category transaction_category,
    metadata jsonb,
    confidence float,
    created_at timestamptz,
    updated_at timestamptz
);
```

## 🌀 Types énumérés

### workflow_state
- `pending` : En attente de traitement
- `document_processing` : Document en cours de traitement
- `transaction_analysis` : Analyse des transactions
- `storage` : Stockage des résultats
- `completed` : Traitement terminé
- `failed` : Échec du traitement

### transaction_category
- `income` : Revenu
- `expense` : Dépense
- `transfer` : Transfert

## 🔑 Sécurité

Les tables sont sécurisées par Row Level Security (RLS) :

### Policies transactions
```sql
-- Lecture limitée aux données de l'utilisateur
create policy "Users can view own transactions"
    on transactions for select
    using (auth.uid()::text = user_id);

-- Accès complet pour le service
create policy "Service can manage all transactions"
    on transactions for all
    using (auth.role() = 'service_role');
```

## 📊 Indexes

### workflows
```sql
create index idx_workflows_user_id on workflows(user_id);
create index idx_workflows_state on workflows(state);
create index idx_workflows_created_at on workflows(created_at);
```

### transactions
```sql
create index idx_transactions_user_id on transactions(user_id);
create index idx_transactions_workflow_id on transactions(workflow_id);
create index idx_transactions_date on transactions(date);
create index idx_transactions_category on transactions(category);
```

## 🔧 Installation

1. Configuration de Supabase CLI :
```bash
npm install -g supabase
supabase login
```

2. Initialisation du projet :
```bash
supabase init
```

3. Exécution des migrations :
```bash
supabase db reset
```

## 📄 Maintenance

### Ajouter une nouvelle migration

1. Créer un nouveau fichier SQL :
```bash
touch migrations/04_new_feature.sql
```

2. Ajouter le code SQL

3. Exécuter la migration :
```bash
supabase db reset
```

### Bonnes pratiques

- Utiliser des noms explicites pour les fichiers
- Préfixer avec numéro de séquence
- Documenter les changements
- Tester les rollbacks
- Vérifier la compatibilité

## ⚙️ Maintenance

- Sauvegarder régulièrement
- Surveiller la taille des tables
- Vérifier les index
- Optimiser les requêtes
- Nettoyer les anciennes données