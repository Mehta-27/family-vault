# 🏦 Family Financial Command Center

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B)
![Supabase](https://img.shields.io/badge/Supabase-Database%20%26%20Auth-3ECF8E)
![Status](https://img.shields.io/badge/Status-Active-success)

A modern, cloud-native application designed to organize, track, and manage a family's entire financial portfolio securely from one place. Features a premium glassmorphism user interface, 24/7 cloud deployment, and secure authentication.

## ✨ Key Features

- **📊 Centralized Dashboard:** Instantly view your total net worth, total asset count, and a categorical distribution of your investments.
- **🔐 Secure Authentication:** Integrated with Supabase Auth to ensure only authorized family members can access financial data.
- **💼 Asset Management:** Easily add, track, and delete assets across various categories (Bank, FD, Mutual Fund, Stock, Insurance, Property, Locker).
- **📄 Document Vault:** Securely upload and store important financial documents (PDFs, images) directly to cloud storage, generating secure URLs for instant viewing.
- **🎨 Elite UI Design:** A sleek, minimal, dark-mode interface featuring subtle animations, a grainy noise layer, and frosted glass elements for a premium user experience.

## 🛠 Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/) (Python)
- **Backend & Database:** [Supabase](https://supabase.com/) (PostgreSQL)
- **Authentication:** Supabase Auth
- **Storage:** Supabase Storage (`vault-documents`)
- **Deployment:** Streamlit Community Cloud

## 🚀 Local Development Setup

To run this application locally, follow these steps:

### 1. Clone the repository
```bash
git clone https://github.com/Mehta-27/family-vault.git
cd family-vault
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Supabase
1. Create a new [Supabase](https://supabase.com/) project.
2. In the SQL Editor, create the `assets` table:
```sql
CREATE TABLE assets (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    institution TEXT,
    value NUMERIC NOT NULL,
    notes TEXT,
    document_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Note: Ensure Row Level Security (RLS) is disabled if using a shared vault setup.
ALTER TABLE assets DISABLE ROW LEVEL SECURITY;
```
3. Create a public storage bucket named `vault-documents`.
4. Create users in the **Authentication** tab.

### 4. Configure Secrets
Create a `.streamlit/secrets.toml` file in the root directory (do **NOT** commit this file):
```toml
[supabase]
url = "YOUR_SUPABASE_PROJECT_URL"
key = "YOUR_SUPABASE_ANON_KEY"
```

### 5. Run the App
```bash
streamlit run app.py
```

## ☁️ Cloud Deployment

This app is optimized for deployment on **Streamlit Community Cloud**.
1. Connect your GitHub repository to Streamlit Cloud.
2. Go to **Advanced Settings**.
3. Paste the contents of your `secrets.toml` file into the Secrets text box.
4. Click Deploy.

## 📝 License
This project is for personal use.

---
*Built with ❤️ for secure and organized family finance management.*
