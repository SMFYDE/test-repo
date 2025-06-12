# 🔍 BlueAxel — Document AI Agent for Tenders

**BlueAxel** is an intelligent agent designed to help analyze and classify documents used in **public or private tenders** (appel d'offre).

It automates the reading, classification, and preparation of tender documents — especially PDFs like Kbis, INSEE files, invoices, etc.

---

## ⚙️ How It Works (Step by Step)

### 1. 🧠 Agent Logic: `blueaxel_agent.py`
This is the main file that starts the process. It connects everything together.

### 2. 🧹 File Preprocessing: `file_preprocessing_pipeline.py`
This module:
- Reads documents (usually PDFs)
- Extracts basic info like title, file size, etc.
- Simplify document with basic process (no big letter, remove date / hours, ...)
- Splits them into **chunks**
- Create vector store with **FAISS**

### 3. 🔗 Graph Execution: `file_graph_orchestration.py`
This file builds the **LangGraph** structure and handles the execution flow.  
It wraps all the model logic into classes and defines **task sequences** for the agent.

### 4. 📂 File Classification: `file_classification_agent.py`
This is the **first agent** that processes files.  
It receives documents and predicts their type (e.g., Kbis, INSEE file, Invoice, etc.)

---

## 📁 Example Document Types

- 🧾 Kbis  
- 📄 INSEE Producer File  
- 📦 Delivery Notes & Invoices  
- ☀️ Photovoltaic Installation Details


#? If you need to add file types, you have two things to do:
#? 1. Add the new type to the `DocumentTypeResponseFormatter` class.
    #? This is where you define the output name of the document write by the agent.

#? 2. Add the new type to the return of `_prompt_build_template` function method in the `FileClassificationAgent` class.
    #? You need to add the new type to the list of document types in the prompt. Explaining the type in the prompt is not mandatory, but it can help the agent to better understand the context and provide a more accurate classification.
