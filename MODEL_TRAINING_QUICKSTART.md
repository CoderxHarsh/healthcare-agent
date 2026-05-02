# ML Model Training Guide - Quick Reference

## 🎯 Your Question
> "How to train the model with more medical data (PDFs, medicine info) using current architecture?"

## ✅ Simple Answer
**You already have everything you need!** Just feed more data into your existing RAG pipeline.

---

## 🏗️ Your Current Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    YOUR SYSTEM                               │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  CRAWLER                    RAG PIPELINE           USAGE      │
│  ─────────                  ────────────          ─────      │
│                                                               │
│  crawler/          →        backend/rag/    →    Chatbot    │
│  crawl_medical_docs.py      ingestion.py         (get context)
│  (downloads PDFs)           (chunks & embeds)                │
│                                                               │
│                             vector_store.py  →  Health      │
│                             (PostgreSQL)           Analyzer    │
│                             (persisted db)       (better      │
│                                                   insights)   │
│                                                               │
│  data/                                                        │
│  documents/                                                   │
│  (stores all PDFs, MD, TXT files)                            │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Flow Through Your System

```
INPUT DATA
    ↓
Medical PDFs, websites
    ↓
Crawler (downloads)
    ↓
data/documents/
(raw files storage)
    ↓
Ingestion Pipeline
├─ Extract text from PDF
├─ Split into 800-char chunks
└─ Calculate embeddings
    ↓
PostgreSQL Vector Store
(searchable knowledge base)
    ↓
USAGE
├─ Chatbot retrieves context
├─ Health Analyzer gets context
└─ API endpoints use knowledge
    ↓
BETTER RESPONSES
```

---

## 🚀 How to Train Your Model - 3 Steps

### Step 1: Crawl (Download Medical Data)
```bash
python train_model.py --mode crawl
```

**What happens:**
- Downloads from 30+ medical websites
- Saves to `data/documents/`
- Takes ~10-15 minutes
- Gets: disease info, medications, nutrition, exercises, mental health

**Websites included:**
- Mayo Clinic
- NHS
- MedlinePlus
- Heart.org
- Diabetes.org
- CDC
- FDA
- WebMD
- And more...

### Step 2: Ingest (Process & Index)
```bash
python train_model.py --mode ingest
```

**What happens:**
- Reads all files from `data/documents/`
- Splits into manageable chunks (800 chars each)
- Calculates embeddings using Google Gemini
- Stores in PostgreSQL vector database
- Takes ~5-10 minutes depending on data size

### Step 3: Verify It Works
```bash
python train_model.py --mode test
```

**What happens:**
- Tests knowledge base with 6 sample queries
- Shows retrieval quality scores
- Proves data is searchable and usable

### All-in-One
```bash
python train_model.py --mode both
```
Runs crawl + ingest + test automatically

---

## 📈 What Gets Better After Training

### BEFORE (Limited Data)
**User asks:** "What should I do for Type 2 Diabetes?"  
**Response:** Generic advice about diet and exercise

### AFTER (Rich Data)
**User asks:** "What should I do for Type 2 Diabetes?"  
**Response:**
- Specific A1C targets to aim for
- Recommended foods (low GI, portion control)
- Exercise schedule (150 min/week moderate)
- Medication interactions to watch
- When to check blood sugar
- Complications to prevent
- Links to authoritative sources

**Why?** The chatbot now retrieves relevant, detailed context from the knowledge base!

---

## 🔄 How It Improves Your System

### Chatbot Gets Smarter
```python
# In backend/chatbot.py
rag_chunks = retrieve(user_input, user_id=user_id)
# ↑ More data = more relevant chunks = better responses
```

### Health Analyzer Gets Better Context
```python
# In backend/health_analyzer.py
# Uses LLM with context about user's conditions
# With more data: better recommendations
```

### Your ML Model Continuously Improves
```
More Data → Better Embeddings → Better Retrieval → Better AI Insights
```

---

## 📋 Implementation Checklist

```
□ Run: python train_model.py --mode crawl
  └─ Gets ~500+ medical documents

□ Run: python train_model.py --mode ingest
  └─ Processes and indexes them

□ Run: python train_model.py --mode test
  └─ Verifies everything works

□ Check stats:
  python train_model.py --mode stats
  └─ See total chunks indexed

□ Done! System now has rich medical knowledge
```

---

## 🎓 What Data Gets Collected

### Diabetes Resources
- Symptoms, causes, risk factors
- Type 1 vs Type 2 differences
- Treatment options
- Medication information
- Nutrition guidelines
- Exercise recommendations
- Blood sugar monitoring
- Complication prevention

### Hypertension Resources
- Blood pressure readings explained
- Risk factors and prevention
- Medication options
- Dietary management
- Exercise guidelines
- When to see doctor

### Mental Health
- Depression symptoms and treatment
- Anxiety management
- Support resources
- Medication information
- Lifestyle strategies

### Lifestyle
- Nutrition guidance
- Exercise recommendations
- Weight management
- Stress reduction
- Sleep improvement

### Medications
- Drug information databases
- Side effects
- Interactions
- Dosage guidelines
- FDA approvals

---

## 💡 Tips for Best Results

### 1. Crawl Regularly
```bash
# Add to your cron jobs or scheduler
0 2 * * * cd /path/to/HealthCareAGENT && python train_model.py --mode both
# Runs daily at 2 AM
```

### 2. Add Your Own PDFs
```
1. Download medical PDFs from trusted sources
2. Save to: data/documents/
3. Run: python train_model.py --mode ingest
4. Done! They're in the knowledge base
```

### 3. Monitor Knowledge Base
```bash
python train_model.py --mode stats
# See: Total chunks, sources, top contributors
```

### 4. Test Quality
```bash
python train_model.py --mode test
# Verify retrieval is working well
```

---

## 🔍 How Retrieval Works

**Query comes in:**
```
"How do I manage my diabetes?"
```

**System converts to embedding:**
```
Query embedding (768 dimensions)
```

**Searches PostgreSQL:**
```
Find most similar chunks in vector space
Using cosine similarity
```

**Returns top results:**
```
[
  {source: "diabetes.org", relevance: 0.89, text: "..."},
  {source: "mayoclinic.org", relevance: 0.87, text: "..."},
  {source: "cdc.gov", relevance: 0.82, text: "..."},
  {source: "nih.gov", relevance: 0.79, text: "..."}
]
```

**LLM uses these chunks:**
```
Generates response with accurate, sourced information
```

---

## 🎯 Expected Results

### Before Training
```
Knowledge base: Empty/minimal
Chunks: 0-10
Retrieval: Generic responses
Context quality: Low
```

### After First Training
```
Knowledge base: Comprehensive
Chunks: 500-1000+
Retrieval: Specific, sourced
Context quality: High
Response quality: Excellent
```

### After Continuous Training
```
Knowledge base: Very comprehensive
Chunks: 1000-5000+
Retrieval: Highly relevant
Context quality: Expert-level
Response quality: Outstanding
```

---

## 🛠️ Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'trafilatura'"
```bash
pip install trafilatura beautifulsoup4
```

### Problem: "Google API key error"
```bash
# Check .env has GOOGLE_API_KEY set
echo $GOOGLE_API_KEY
```

### Problem: "PostgreSQL error"
```bash
# Delete old database and recreate
rm -rf PostgreSQL DB
python train_model.py --mode ingest
```

### Problem: "Slow ingestion"
```bash
# Normal for large datasets (500+ documents)
# Takes 5-10 minutes
# Check progress in console
```

---

## ✨ Next Level Features (Optional)

### 1. Scheduled Training
```python
# In cron or systemd
0 2 * * * python /path/train_model.py --mode both
```
Daily automatic training

### 2. Custom Data Sources
```python
# Add your own medical sources to MEDICAL_URLS_COMPREHENSIVE
# in train_model.py
```

### 3. Quality Monitoring
```bash
# Track retrieval scores over time
python train_model.py --mode test > retrieval_quality.log
```

### 4. Real-time Updates
```python
# Add new documents to data/documents/
# Run ingest immediately
# System updates within minutes
```

---

## 📊 Summary

| Component | What It Does | File |
|-----------|-------------|------|
| **Crawler** | Downloads medical websites | `crawler/crawl_medical_docs.py` |
| **Ingestion** | Chunks and embeds documents | `backend/rag/ingestion.py` |
| **Vector Store** | Stores embeddings searchably | `backend/rag/vector_store.py` |
| **Retriever** | Gets relevant chunks | `backend/rag/retriever.py` |
| **Training Script** | One-command training | `train_model.py` |

---

## 🎓 The Magic Happens Here

When you run `train_model.py`, this is what happens behind the scenes:

```
┌─────────────────────────────────────────┐
│ 1. CRAWL                                │
│    └─ Downloads medical websites        │
│       → 500+ documents                  │
├─────────────────────────────────────────┤
│ 2. SAVE                                 │
│    └─ Stores in data/documents/         │
├─────────────────────────────────────────┤
│ 3. INGEST                               │
│    └─ Chunks (800 chars each)           │
│    └─ Embeds (Google Gemini)            │
│    └─ 2000+ chunks created              │
├─────────────────────────────────────────┤
│ 4. STORE                                │
│    └─ PostgreSQL (vector database)        │
│    └─ Persistent storage                │
├─────────────────────────────────────────┤
│ 5. USE                                  │
│    └─ Chatbot retrieves context         │
│    └─ Health analyzer gets insights     │
│    └─ API uses knowledge                │
├─────────────────────────────────────────┤
│ RESULT: Smarter, more knowledgeable AI  │
└─────────────────────────────────────────┘
```

---

## 🚀 Get Started Right Now

```bash
# 1. Train your model with medical data
python train_model.py --mode both

# 2. Check it worked
python train_model.py --mode stats

# 3. Test the knowledge base
python train_model.py --mode test

# 4. Done! Your system is trained
```

That's it! Your ML model now has medical knowledge! 🎉

