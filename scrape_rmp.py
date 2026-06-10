"""
RMP Scraper for CCNY EE Professors
"""

import os
import time
import base64
import requests

OUTPUT_DIR = "rmp_professor_files"

PROFESSORS = [
    {"name": "Andrii Golovin",        "id": "1823726"},
    {"name": "Joseph Barba",           "id": "1937184"},
    {"name": "Liubov Kreminska",       "id": "2071926"},
    {"name": "Nidal Khrais",           "id": "802899"},
    {"name": "Ping-Pei Ho",            "id": "288006"},
    {"name": "Julio Reyes",            "id": "1199855"},
    {"name": "M. Umit Uyar",           "id": "519308"},
    {"name": "Ali Duale",              "id": "1962765"},
    {"name": "Yi Sun",                 "id": "288005"},
    {"name": "Roger Dorsinville",      "id": "287999"},
    {"name": "Samah Saeed",            "id": "2839499"},
    {"name": "Alfredo Cano Martinez",  "id": "2132415"},
    {"name": "Hakan Pekcan",           "id": "2129998"},
    {"name": "Sang-Woo Seo",           "id": "1274141"},
    {"name": "Bruce Kim",              "id": "2005606"},
    {"name": "Edward Baurin",          "id": "1274143"},
]

GQL_URL = "https://www.ratemyprofessors.com/graphql"

HEADERS = {
    "Authorization": "Basic dGVzdDp0ZXN0",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.ratemyprofessors.com/",
    "Origin": "https://www.ratemyprofessors.com",
    "Accept": "*/*",
    "Cookie": "_pubcid=419c775f-4f6c-4290-b3e4-c7a72d1b043c; RMP_AUTH_COOKIE_VERSION=v02; cid=Gh4R3klevs-20260609; AWSALB=44VOYK8OukUyyJWnfLnzXPyDW3AGveio4kGgI1RIQxMTRtd97I3lfJ1TODC+u+yzEWw2TbEEORe2i6Nkq2MO7AbmMLt4WfkHT6NgOge3RFB+V9Rhc5pn28JGrFKC; AWSALBCORS=44VOYK8OukUyyJWnfLnzXPyDW3AGveio4kGgI1RIQxMTRtd97I3lfJ1TODC+u+yzEWw2TbEEORe2i6Nkq2MO7AbmMLt4WfkHT6NgOge3RFB+V9Rhc5pn28JGrFKC; gc_session_id=5advh3ybm7tqzqvh63nnh",
}

STATS_QUERY = """
query GetTeacherStats($id: ID!) {
  node(id: $id) {
    ... on Teacher {
      legacyId
      firstName
      lastName
      department
      avgRating
      avgDifficulty
      numRatings
      wouldTakeAgainPercent
      school { name city state }
    }
  }
}
"""

RATINGS_QUERY = """
query GetTeacherRatings($id: ID!, $count: Int!, $cursor: String) {
  node(id: $id) {
    ... on Teacher {
      ratings(first: $count, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        edges {
          node {
            date
            class
            comment
            clarityRating
            helpfulRating
            difficultyRating
            wouldTakeAgain
            grade
            isForOnlineClass
            attendanceMandatory
          }
        }
      }
    }
  }
}
"""


def encode_id(legacy_id):
    return base64.b64encode(f"Teacher-{legacy_id}".encode()).decode()


def gql(query, variables):
    resp = requests.post(
        GQL_URL,
        headers=HEADERS,
        json={"query": query, "variables": variables},
        timeout=20,
    )
    resp.raise_for_status()
    result = resp.json()
    if result.get("errors"):
        raise Exception(result["errors"][0]["message"])
    return result.get("data", {}).get("node") or {}


def fetch_all_reviews(encoded_id):
    reviews = []
    cursor = None
    while True:
        node = gql(RATINGS_QUERY, {"id": encoded_id, "count": 100, "cursor": cursor})
        ratings = node.get("ratings", {})
        edges = ratings.get("edges", [])
        reviews.extend(edges)
        page_info = ratings.get("pageInfo", {})
        if not page_info.get("hasNextPage"):
            break
        cursor = page_info.get("endCursor")
        time.sleep(0.3)
    return reviews


def fmt(prof_meta, stats, reviews):
    name = prof_meta["name"]
    url = f"https://www.ratemyprofessors.com/professor/{prof_meta['id']}"

    school = (stats.get("school") or {}).get("name", "N/A")
    dept = stats.get("department", "N/A")
    avg_r = stats.get("avgRating", "N/A")
    avg_d = stats.get("avgDifficulty", "N/A")
    n = stats.get("numRatings", 0)
    wta = stats.get("wouldTakeAgainPercent", -1)
    wta_s = f"{round(wta)}%" if (wta is not None and wta >= 0) else "N/A"

    lines = [
        f"Professor: {name}",
        "=" * 60,
        f"School:              {school}",
        f"Department:          {dept}",
        f"RMP URL:             {url}",
        f"Overall Rating:      {avg_r} / 5.0",
        f"Difficulty:          {avg_d} / 5.0",
        f"Would Take Again:    {wta_s}",
        f"Number of Ratings:   {n}",
        "",
    ]

    if not reviews:
        lines.append("No individual reviews available.")
        return "\n".join(lines)

    lines.append(f"Reviews ({len(reviews)} total)")
    lines.append("-" * 60)

    for i, edge in enumerate(reviews, 1):
        r = edge.get("node", {})
        date    = r.get("date", "N/A")
        course  = r.get("class") or "N/A"
        comment = (r.get("comment") or "").strip() or "[no comment]"
        clarity = r.get("clarityRating", "N/A")
        helpful = r.get("helpfulRating", "N/A")
        diff    = r.get("difficultyRating", "N/A")
        wta_r   = r.get("wouldTakeAgain")
        wta_rs  = "Yes" if wta_r == 1 else ("No" if wta_r == 0 else "N/A")
        grade   = r.get("grade") or "N/A"
        attend  = r.get("attendanceMandatory") or "N/A"
        online  = "Yes" if r.get("isForOnlineClass") else "No"

        lines += [
            f"\nReview #{i}",
            f"  Date:              {date}",
            f"  Course:            {course}",
            f"  Clarity: {clarity}/5  |  Helpful: {helpful}/5  |  Difficulty: {diff}/5",
            f"  Would Take Again:  {wta_rs}  |  Grade: {grade}  |  Online: {online}",
            f"  Attendance:        {attend}",
            f"  Comment: {comment}",
        ]

    return "\n".join(lines)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Output directory: {OUTPUT_DIR}/\n")

    for prof in PROFESSORS:
        print(f"Fetching: {prof['name']} ...")
        encoded_id = encode_id(prof["id"])

        try:
            stats = gql(STATS_QUERY, {"id": encoded_id})
            reviews = fetch_all_reviews(encoded_id)
            content = fmt(prof, stats, reviews)
            status = f"rating={stats.get('avgRating','?')}, reviews={len(reviews)}"
        except Exception as e:
            print(f"  ERROR: {e}")
            content = f"Professor: {prof['name']}\nERROR: {e}\n"
            status = "ERROR"

        filename = (
            prof["name"].lower()
            .replace(" ", "_")
            .replace(".", "")
            .replace("/", "_")
            + ".txt"
        )
        path = os.path.join(OUTPUT_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"  -> {path}  ({status})")
        time.sleep(0.5)

    print(f"\nAll done! {len(PROFESSORS)} files in ./{OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
