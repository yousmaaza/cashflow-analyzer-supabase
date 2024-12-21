# CashFlow Analyzer - Supabase Version

Service d'analyse de relevés bancaires utilisant Python et Supabase.

## 📊 Description

Ce projet est une version microservices du CashFlow Analyzer, utilisant Supabase comme backend. Il permet d'analyser les relevés bancaires en PDF en extrayant automatiquement les transactions et en fournissant des analyses détaillées.

## 🏗 Architecture

Le projet est organisé en trois services principaux :

### 1. Document Processor Service
- Conversion des PDF en images
- Détection des tableaux avec YOLO
- Extraction du texte avec OCR
- Structured data extraction

### 2. Transaction Analyzer Service
- Analyse des transactions
- Catégorisation automatique
- Détection des patterns
- Génération de statistiques

### 3. Data Manager Service
- Interface avec Supabase
- Gestion des données
- API CRUD
- Cache management

## 🛠 Technologies

- Python 3.10+
- Supabase
- OCR: doctr
- PDF Processing: pdf2image
- Table Detection: YOLOv8
- Data Analysis: pandas, numpy

## 📝 Configuration Supabase

### Tables Required:

```sql
-- Documents table
create table documents (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references auth.users,
  filename text,
  status text,
  created_at timestamp with time zone default timezone('utc'::text, now())
);

-- Transactions table
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
```

## 🚀 Installation

1. Clone the repository
```bash
git clone https://github.com/yousmaaza/cashflow-analyzer-supabase.git
cd cashflow-analyzer-supabase
```

2. Set up Python environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure Supabase
```bash
# Copy .env.example to .env and fill in your Supabase details
cp .env.example .env
```

## 🏃‍♂️ Running the Services

Each service can be run independently using Docker:

```bash
docker-compose up document-processor
docker-compose up transaction-analyzer
docker-compose up data-manager
```

## 🧪 Tests

```bash
pytest tests/
```

## 📚 Documentation

Detailed documentation for each service can be found in their respective directories:
- [Document Processor](services/document-processor/README.md)
- [Transaction Analyzer](services/transaction-analyzer/README.md)
- [Data Manager](services/data-manager/README.md)

## 📄 License

MIT

## 👥 Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request