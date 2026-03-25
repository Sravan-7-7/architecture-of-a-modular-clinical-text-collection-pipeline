🏥 Architecture of a Modular Clinical Text Collection System

This repository outlines the structural design and modular framework for a Clinical Data Retrieval System. The architecture is designed to handle up to 500+ doctor prescriptions, converting unstructured clinical text into a searchable, indexed database for healthcare providers.

🏗️ System Architecture

The system is built using a Modular Design Pattern, separating data ingestion from the search interface to ensure scalability and ease of maintenance.

1. Data Ingestion Layer (The "Input")

Source: Manual entry or OCR (Optical Character Recognition) of 105 doctor prescriptions.

Normalization: Standardizing medical terminology (e.g., converting "Paracetamol" and "Acetaminophen" to a unified ID).

Storage: Data is structured into Clinical_Data.csv or a local SQLite database.


2. Processing Module (The "Engine")

1.Indexing: Utilizing Pandas to set unique identifiers (e.g., Patient_ID or Name) for $O(1)$ lookup time.

2. Validation: Ensuring data integrity by checking for null values or invalid medical codes before storage.

3. Retrieval Interface (The "Output")
   
1.Search Algorithm: A Python-based query engine that handles user input.

2.Error Handling: Implements try-except blocks to manage "Patient Not Found" scenarios without system crashes.

🛠️ Modular Components

1.downloader.py

2.scraper.py

3.extractor.py

4.filter.py

5.storage
