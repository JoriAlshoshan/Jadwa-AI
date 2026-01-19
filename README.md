# Jadwa AI – Business Feasibility Analysis System

**Jadwa AI** is a web-based business feasibility analysis system developed as a **graduation project**.  
The system combines **Machine Learning** and **Generative AI** to help Saudi entrepreneurs evaluate the feasibility of their business ideas and receive clear, actionable recommendations before implementation.

The platform aims to reduce uncertainty, support informed decision-making, and provide an accessible alternative to traditional feasibility studies.

---

## System Roles

| Role | Description |
|-----|-------------|
| Entrepreneur | Submits project details and receives feasibility analysis and recommendations |
| System Admin | Manages users, projects, and system data |

---

## Key Features

### 1. User Authentication
- Secure login, registration, and logout
- Protected access to user projects and analysis results
- Session-based authentication

### 2. Project Data Collection
- Interactive form for entering project details, including:
  - Project type (Service / Product / Hybrid)
  - Region (Saudi Arabia)
  - Project budget (SAR)
  - Project duration
  - Number of Saudi employees
  - Market and economic indicators

### 3. Feasibility Prediction (Machine Learning)
- Uses a **Random Forest** classification model
- Trained on a structured dataset relevant to the Saudi market
- Produces a **feasibility probability score** for each project

### 4. Decision Logic (Dynamic Threshold)
- Applies adaptive decision thresholds based on project budget:
  - Small projects → lower threshold (encourage experimentation)
  - Medium projects → balanced threshold
  - Large projects → stricter threshold (risk reduction)
- Final decision:
  - **Feasible**
  - **Not Feasible**

### 5. AI-Based Recommendations (Generative AI)
- Generates structured, business-friendly recommendations
- Output sections include:
  - Summary
  - Strengths
  - Risks
  - Action Plan
  - Budget & Market Suggestions
  - Next Steps
- Language is non-technical and suitable for entrepreneurs
- Uses prompt-based fine-tuned Generative AI behavior

### 6. Results Dashboard
- Displays feasibility score and final decision
- Shows AI-generated recommendations clearly
- Designed for non-technical users
- Supports future expansion to downloadable feasibility reports (PDF)

---

## Project Goal

This project was developed to:
- Apply **Machine Learning** techniques to real-world feasibility analysis
- Integrate **Generative AI** for intelligent decision support
- Build a complete **AI-powered web-based system**
- Support entrepreneurs with data-driven insights
- Demonstrate practical AI and web integration in a graduation project

---

## System Architecture (High Level)

- **Frontend:** Web-based user interface
- **Backend:** Django framework
- **AI Components:**
  - Random Forest feasibility prediction model
  - Dynamic decision threshold logic
  - Prompt-based fine-tuned Generative AI
- **Database:** Stores users, projects, and analysis results
- **Cloud Platform:** Microsoft Azure

---

## Deployment

The Jadwa AI system is designed to be deployed on **Microsoft Azure**, providing a scalable and secure cloud environment for hosting the web application, AI services, and database components.  
Cloud deployment ensures reliability, real-world applicability, and future scalability of the system.

---

## Technologies Used

- Python
- Scikit-learn
- Django
- OpenAI API
- HTML / CSS / JavaScript
- Microsoft Azure
- Git / GitHub

---

## Team Members

**Jori Alshoshan** - jori.alshoshan@gmail.com  

**Rahaf Alharbi** - r22581919@gmail.com
  
**Sura Alkuzaim** - sura.abdullah2003@gmail.com

---

© 2026 Jadwa AI 
