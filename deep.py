import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")

# Endpoints
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
SERPAPI_URL = "https://serpapi.com/search"

# Model configuration
DEFAULT_MODEL = "anthropic/claude-3.5-haiku"

# ============================
# Asynchronous Helper Functions
# ============================

async def call_openrouter_async(session, messages, model=DEFAULT_MODEL):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "X-Title": "OpenDeepResearcher, by Matt Shumer",
        "Content-Type": "application/json"
    }
    payload = {"model": model, "messages": messages}
    try:
        async with session.post(OPENROUTER_URL, headers=headers, json=payload) as resp:
            if resp.status == 200:
                result = await resp.json()
                print("OpenRouter raw response:", result)
                try:
                    return result['choices'][0]['message']['content']
                except (KeyError, IndexError) as e:
                    print("Unexpected OpenRouter response structure:", result)
                    return None
            else:
                text = await resp.text()
                print(f"OpenRouter API error: {resp.status} - {text}")
                return None
    except Exception as e:
        print("Error calling OpenRouter:", e)
        return None

async def generate_search_queries_async(session, user_query):
    prompt = (
        "You are an expert research assistant. Given the user's query, generate up to four distinct, "
        "precise search queries that would help gather comprehensive information on the topic. "
        "Return only a Python list of strings, for example: ['query1', 'query2', 'query3']." 
    )
    messages = [
        {"role": "system", "content": "You are a helpful and precise research assistant."},
        {"role": "user", "content": f"User Query: {user_query}\n\n{prompt}"}
    ]
    response = await call_openrouter_async(session, messages)
    print("LLM search queries raw response:", response)
    if response:
        try:
            search_queries = eval(response)
            if isinstance(search_queries, list):
                print("Parsed search queries:", search_queries)
                return search_queries
            else:
                print("LLM did not return a list. Response:", response)
                return []
        except Exception as e:
            print("Error parsing search queries:", e, "\nResponse:", response)
            return []
    return []

async def perform_search_async(session, query):
    params = {"q": query, "api_key": SERPAPI_API_KEY, "engine": "google"}
    try:
        async with session.get(SERPAPI_URL, params=params) as resp:
            if resp.status == 200:
                results = await resp.json()
                print(f"SERPAPI results for query '{query}':", results)
                if "organic_results" in results:
                    links = [item.get("link") for item in results["organic_results"] if "link" in item]
                    return links
                else:
                    print("No organic results in SERPAPI response.")
                    return []
            else:
                text = await resp.text()
                print(f"SERPAPI error: {resp.status} - {text}")
                return []
    except Exception as e:
        print("Error performing SERPAPI search:", e)
        return []

async def batch_fetch_webpages_async(session, urls):
    """
    Batch scrape multiple URLs using FireCrawl's synchronous batch scrape method.
    This function runs in a thread via asyncio.to_thread.
    """
    try:
        from firecrawl import FireCrawlApp
        app = FireCrawlApp(api_key=FIRECRAWL_API_KEY)
        # Set formats to get both markdown and html (adjust as needed)
        params = {'formats': ['markdown', 'html']}
        # Call the synchronous batch scrape in a thread
        result = await asyncio.to_thread(app.batch_scrape_urls, urls, params)
        print("Batch scrape result:", result)
        pages = {}
        data_list = result.get("data", [])
        # Assume order of results matches the order of URLs
        for idx, url in enumerate(urls):
            if idx < len(data_list):
                item = data_list[idx]
                # Prefer markdown content, fallback to html if markdown is empty
                content = item.get("markdown") or item.get("html") or ""
                pages[url] = content
            else:
                pages[url] = ""
        return pages
    except Exception as e:
        print("Error during batch scraping:", e)
        return {}

async def is_page_useful_async(session, user_query, page_text):
    prompt = (
        "You are a critical research evaluator. Given the user's query and the content of a webpage, "
        "determine if the webpage contains information relevant and useful for addressing the query. "
        "Respond with exactly one word: 'Yes' if the page is useful, or 'No' if it is not. Do not include any extra text."
    )
    messages = [
        {"role": "system", "content": "You are a strict and concise evaluator of research relevance."},
        {"role": "user", "content": f"User Query: {user_query}\n\nWebpage Content (first 20000 characters):\n{page_text[:20000]}\n\n{prompt}"}
    ]
    response = await call_openrouter_async(session, messages)
    print("Is-page-useful LLM response:", response)
    if response:
        answer = response.strip()
        if answer in ["Yes", "No"]:
            return answer
        else:
            if "Yes" in answer:
                return "Yes"
            elif "No" in answer:
                return "No"
    return "No"

async def extract_relevant_context_async(session, user_query, search_query, page_text):
    prompt = (
        "You are an expert information extractor. Given the user's query, the search query that led to this page, "
        "and the webpage content, extract all pieces of information that are relevant to answering the user's query. "
        "Return only the relevant context as plain text without commentary."
    )
    messages = [
        {"role": "system", "content": "You are an expert in extracting and summarizing relevant information."},
        {"role": "user", "content": f"User Query: {user_query}\nSearch Query: {search_query}\n\nWebpage Content (first 20000 characters):\n{page_text[:20000]}\n\n{prompt}"}
    ]
    response = await call_openrouter_async(session, messages)
    print("Extracted context raw response:", response)
    if response:
        return response.strip()
    return ""

async def get_new_search_queries_async(session, user_query, previous_search_queries, all_contexts):
    context_combined = "\n".join(all_contexts)
    prompt = (
        "You are an analytical research assistant. Based on the original query, the search queries performed so far, "
        "and the extracted contexts from webpages, determine if further research is needed. "
        "If further research is needed, provide up to four new search queries as a Python list (for example, "
        "['new query1', 'new query2']). If you believe no further research is needed, respond with exactly ."
        "\nOutput only a Python list or the token  without any additional text."
    )
    messages = [
        {"role": "system", "content": "You are a systematic research planner."},
        {"role": "user", "content": f"User Query: {user_query}\nPrevious Search Queries: {previous_search_queries}\n\nExtracted Relevant Contexts:\n{context_combined}\n\n{prompt}"}
    ]
    response = await call_openrouter_async(session, messages)
    print("New search queries raw response:", response)
    if response:
        cleaned = response.strip()
        if cleaned == "":
            return ""
        try:
            new_queries = eval(cleaned)
            if isinstance(new_queries, list):
                return new_queries
            else:
                print("LLM did not return a list for new search queries. Response:", response)
                return []
        except Exception as e:
            print("Error parsing new search queries:", e, "\nResponse:", response)
            return []
    return ""

async def generate_final_report_async(session, user_query, all_contexts):
    context_combined = "\n".join(all_contexts)
    prompt = (
        "You are an expert researcher and report writer. Based on the gathered contexts below and the original query, "
        "write a comprehensive, well-structured, and detailed report that addresses the query thoroughly. "
        "Include all relevant insights and conclusions without extraneous commentary."
    )
    messages = [
        {"role": "system", "content": "You are a skilled report writer."},
        {"role": "user", "content": f"User Query: {user_query}\n\nGathered Relevant Contexts:\n{context_combined}\n\n{prompt}"}
    ]
    report = await call_openrouter_async(session, messages)
    print("Final report raw response:", report)
    return report

# =========================
# Main Asynchronous Routine
# =========================

async def async_main():
    user_query = input("Enter your research query/topic: ").strip()
    iter_limit_input = input("Enter maximum number of iterations (default 10): ").strip()
    iteration_limit = int(iter_limit_input) if iter_limit_input.isdigit() else 10

    aggregated_contexts = []  # All useful contexts from every iteration
    all_search_queries = []   # Every search query used across iterations
    iteration = 0

    async with aiohttp.ClientSession() as session:
        # ----- INITIAL SEARCH QUERIES -----
        new_search_queries = await generate_search_queries_async(session, user_query)
        if not new_search_queries:
            print("No search queries were generated by the LLM. Exiting.")
            return
        all_search_queries.extend(new_search_queries)

        # ----- ITERATIVE RESEARCH LOOP -----
        while iteration < iteration_limit:
            print(f"\n=== Iteration {iteration + 1} ===")
            iteration_contexts = []

            # For each search query, perform SERPAPI searches concurrently.
            search_tasks = [perform_search_async(session, query) for query in new_search_queries]
            search_results = await asyncio.gather(*search_tasks)

            # Aggregate all unique links from all search queries of this iteration.
            unique_links = {}
            for idx, links in enumerate(search_results):
                query = new_search_queries[idx]
                for link in links:
                    if link not in unique_links:
                        unique_links[link] = query

            print(f"Aggregated {len(unique_links)} unique links from this iteration.")

            # --- BATCH SCRAPE: Fetch all pages at once ---
            urls = list(unique_links.keys())
            batch_pages = await batch_fetch_webpages_async(session, urls)
            for url in urls:
                page_text = batch_pages.get(url, "")
                print(f"Fetched content from: {url} (length: {len(page_text)})")
                if not page_text:
                    print(f"No content for {url}")
                    continue
                usefulness = await is_page_useful_async(session, user_query, page_text)
                print(f"Page usefulness for {url}: {usefulness}")
                if usefulness == "Yes":
                    context = await extract_relevant_context_async(session, user_query, unique_links[url], page_text)
                    if context:
                        print(f"Extracted context from {url} (first 200 chars): {context[:200]}")
                        iteration_contexts.append(context)

            if iteration_contexts:
                aggregated_contexts.extend(iteration_contexts)
            else:
                print("No useful contexts were found in this iteration.")

            new_search_queries = await get_new_search_queries_async(session, user_query, all_search_queries, aggregated_contexts)
            if new_search_queries == "":
                print("LLM indicated that no further research is needed.")
                break
            elif new_search_queries:
                print("LLM provided new search queries:", new_search_queries)
                all_search_queries.extend(new_search_queries)
            else:
                print("LLM did not provide any new search queries. Ending the loop.")
                break

            iteration += 1

        print("\nGenerating final report...")
        final_report = await generate_final_report_async(session, user_query, aggregated_contexts)
        print("\n==== FINAL REPORT ====\n")
        print(final_report)

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
