import requests
from bs4 import BeautifulSoup
import urllib.parse as up
import pandas as pd
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
}

def build_search_url(query, location, start=0, geo_id=None, current_job_id=None):
    base = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    params = {"keywords": query, "location": location, "start": str(start)}
    if geo_id: params["geoId"] = str(geo_id)
    if current_job_id: params["currentJobId"] = str(current_job_id)
    return f"{base}?{up.urlencode(params)}"

def parse_job_ids(html):
    soup = BeautifulSoup(html, "html.parser")
    ids = []
    for li in soup.find_all("li"):
        card = li.find("div", {"class": "base-card"})
        if not card: continue
        urn = card.get("data-entity-urn")
        if not urn or ":" not in urn: continue
        parts = urn.split(":")
        if len(parts) >= 4:
            ids.append(parts[3])
    return ids

def extract_text(el):
    if not el: return None
    # Normalize whitespace and strip
    return " ".join(el.get_text(separator=" ", strip=True).split())

def fetch_job_detail(job_id):
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    data = {"job_id": job_id}

    # Company name from logo alt
    try:
        data["company"] = soup.find("div", {"class": "top-card-layout__card"}).find("a").find("img").get("alt")
    except Exception:
        data["company"] = None

    # Job title
    try:
        data["job_title"] = soup.find("div", {"class": "top-card-layout__entity-info"}).find("a").get_text(strip=True)
    except Exception:
        data["job_title"] = None

    # Seniority level (first criteria)
    try:
        crit = soup.find("ul", {"class": "description__job-criteria-list"}).find("li")
        data["level"] = crit.get_text(strip=True).replace("Seniority level", "").strip()
    except Exception:
        data["level"] = None

    # Job description (expanded HTML container usually uses show-more-less-html)
    # Try multiple likely containers to be resilient
    jd_text = None
    for selector in [
        "div.show-more-less-html__markup",              # inner markup
        "div.show-more-less-html",                      # wrapper
        "div.description__text",                        # legacy
        "section.description",                          # fallback
    ]:
        el = soup.select_one(selector)
        jd_text = extract_text(el)
        if jd_text: break
    data["job_description"] = jd_text

    # Company description snippet (if present on job page)
    # Often appears near the company top card or aside as 'about' text
    comp_desc = None
    for selector in [
        "div.top-card-layout__card span.topcard__flavor",         # small about line
        "div.top-card-layout__entity-info p",                     # short blurb
        "section.about-us__content div",                          # rare variant
        "div.jobs-unified-top-card__subtitle-primary-group",      # group text
    ]:
        el = soup.select_one(selector)
        comp_desc = extract_text(el)
        if comp_desc: break
    data["company_description"] = comp_desc

    return data

def scrape_first_n_jobs(query, location, n=20, page_step=25, geo_id=None):
    results, seen = [], set()
    start = 0
    while len(results) < n:
        url = build_search_url(query, location, start=start, geo_id=geo_id)
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code != 200 or not r.text.strip():
            break
        ids = parse_job_ids(r.text)
        if not ids:
            break
        for jid in ids:
            if jid in seen: continue
            seen.add(jid)
            try:
                detail = fetch_job_detail(jid)
                results.append(detail)
            except Exception:
                continue
            if len(results) >= n:
                break
            time.sleep(0.5)
        start += page_step
        time.sleep(0.8)
    return results[:n]

if __name__ == "__main__":
    query = "Software Engineer"              # change as needed
    location = "London, United Kingdom"   # change as needed

    rows = scrape_first_n_jobs(query, location, n=100, page_step=25, geo_id=None)
    df = pd.DataFrame(rows)
    df.to_csv("linkedinjobs_first20_with_desc.csv", index=False, encoding="utf-8")
    print(df.head(5))
