import os
from dotenv import load_dotenv
from serpapi import GoogleSearch

load_dotenv()
API_KEY = os.getenv("SERPAPI_API_KEY")

def serp_search(query, tbm=None):
    """Call SerpAPI and return JSON results."""
    params = {
        "engine": "google",
        "q": query,
        "api_key": API_KEY,
        "num": 10,
        "gl": "in",
    }
    if tbm: 
        params["tbm"] = tbm
    search = GoogleSearch(params)
    return search.get_dict()

def extract_company_info(company):
    facts = {}
    
    data = serp_search(f"{company} company profile")
    kg = data.get("knowledge_graph", {})
    if kg:
        facts["name"] = kg.get("title", company)
        facts["industry"] = kg.get("type", "Unknown")
        facts["founded"] = kg.get("founded_date", "N/A")
        facts["headquarters"] = kg.get("headquarters", "N/A")
        facts["employees"] = kg.get("employees", "N/A")
    
    return facts

def extract_latest_news(company):
    news_data = serp_search(f"{company} latest news", tbm="nws")
    headlines = []
    for item in news_data.get("news_results", [])[:3]:
        headlines.append(f"{item.get('title')} ({item.get('date')})")
    return headlines

def extract_role_details(company, role):
    role_facts = {"skills": [], "experience": "", "salary": "Not disclosed"}
    role_data = serp_search(f"{company} {role} job description")
    
    for result in role_data.get("organic_results", [])[:5]:
        snippet = result.get("snippet", "").lower()
        if "experience" in snippet and not role_facts["experience"]:
            role_facts["experience"] = snippet
        if any(word in snippet for word in ["python", "sql", "java", "excel", "communication", "leadership"]):
            role_facts["skills"].append(snippet)
    
    salary_data = serp_search(f"{role} salary at {company}")
    for res in salary_data.get("organic_results", []):
        if "$" in res.get("snippet", "") or "₹" in res.get("snippet", ""):
            role_facts["salary"] = res.get("snippet")
            break
    
    return role_facts

def main():
    company = input("Enter Company Name: ")
    role = input("Enter Job Role: ")

    company_facts = extract_company_info(company)
    latest_news = extract_latest_news(company)
    role_details = extract_role_details(company, role)

    print("\nCompany Overview")
    for k, v in company_facts.items():
        print(f"{k.capitalize()}: {v}")
    
    print("\nLatest News")
    for news in latest_news:
        print(f"- {news}")
    
    print("\nRole Requirements")
    print("Skills:", role_details["skills"])
    print("Experience:", role_details["experience"])
    print("Salary Range:", role_details["salary"])

if __name__ == "__main__":
    main()
