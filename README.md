# 🚀 ResumeIQAI

An AI-powered ATS Resume Analyzer built with React, FastAPI and Groq LLaMA 3.3 70B.

## Features

- 📄 Upload Resume (PDF)
- 🤖 AI Resume Feedback
- 📊 ATS Score
- 🎯 Skill Match Analysis
- ❌ Missing Skills Detection
- 💡 Resume Improvement Suggestions
- 📑 Resume Section Analysis
- 📥 Download Professional PDF Report# ResumeIQ AI

> An AI-powered ATS resume analyzer that helps job seekers optimize their resumes using LLaMA 3.3 70B (via Groq API) — built as a full-stack SaaS application.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat&logo=vite&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLaMA%203.3%2070B-orange?style=flat)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Overview

ResumeIQ AI analyzes resumes against job descriptions the way an Applicant Tracking System (ATS) would, then gives candidates clear, actionable feedback to improve their match score. It combines a FastAPI backend with an LLM-powered analysis engine and a React/Vite frontend for a smooth, real-time user experience.

## Demo

> Screenshots/GIF coming soon — project is currently run locally, deployment in progress.

<!-- Add screenshots here once ready, e.g.: -->
<!-- ![Dashboard Screenshot](./docs/screenshot-dashboard.png) -->

## Features

- **ATS Match Scoring** — analyzes resume against a job description and generates a compatibility score
- **Skill Gap Detection** — identifies missing keywords/skills compared to the job description
- **AI-Powered Suggestions** — uses LLaMA 3.3 70B via Groq API to suggest concrete resume improvements
- **PDF Report Generation** — generates a downloadable, formatted PDF report of the analysis
- **Clean, Responsive UI** — built with React + Vite for a fast, modern experience

## Tech Stack

**Frontend:** React, Vite, JavaScript, CSS
**Backend:** FastAPI (Python)
**AI/LLM:** Groq API — LLaMA 3.3 70B
**Other:** ReportLab (PDF generation)

## How It Works

1. User uploads their resume and pastes a target job description
2. Backend extracts and parses resume content
3. Resume + job description are sent to LLaMA 3.3 70B (via Groq API) for analysis
4. The model returns a match score, missing skills, and improvement suggestions
5. Results are displayed in the UI and can be downloaded as a PDF report

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- A [Groq API key](https://console.groq.com/)

### Backend Setup

```bash
cd Backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create a `.env` file in the `Backend` folder:

```
GROQ_API_KEY=your_groq_api_key_here
```

Run the backend:

```bash
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd Frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173` (frontend) and `http://localhost:8000` (backend API).

## Roadmap

- [ ] Deploy backend on Railway, frontend on Vercel, database on Supabase
- [ ] Job Application Tracker
- [ ] Interview Prep AI — generates mock interview questions from resume + JD
- [ ] Resume Bullet Point Improver

## Author

**Shyama Mishra**
B.Tech CSE (Data Science), Galgotias College of Engineering & Technology
[GitHub](https://github.com/shyama230706) · [LinkedIn](https://linkedin.com/in/shyama-mishra-50980628)

## License

This project is licensed under the MIT License.




