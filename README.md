# IrisLens: Your AI-Powered Research Assistant

**🚀 A lightweight, modular, and FireCrawl-powered research assistant built to automate deep web research. Inspired by OpenAI’s DeepResearch, but a shittier, funnier, and cheaper alternative.**

---

## 🧠 What is IrisLens?

IrisLens is an AI-driven research automation tool that:

- 🔍 **Generates precise search queries** based on a given topic.
- 🌍 **Scans the web** for the most relevant sources.
- 📄 **Extracts structured data** (titles, descriptions, summaries) from multiple URLs using FireCrawl's Batch Scrape API.
- 🤖 **Filters and refines results** to determine useful content.
- 📝 **Compiles a structured research report** from the extracted data.

**All of this happens asynchronously** for maximum efficiency using OpenRouter (Claude/GPT-4o/DeepSeek).

---

## ⚙️ How It Works

1️⃣ **Query Expansion**  
IrisLens takes a user’s query and uses LLM-powered prompt engineering to generate precise search terms for better web research.

2️⃣ **Batch Web Scraping**  
It then:  
- Uses **FireCrawl's Batch Scrape API** to fetch structured data from relevant URLs.  
- Extracts titles, summaries, and key metadata for processing.

3️⃣ **Intelligent Filtering & Ranking**  
After scraping, the assistant:  
- Filters out useless content (SEO spam, irrelevant pages).  
- Uses an **LLM-based scoring system** to rank sources based on quality & relevance.

4️⃣ **Final Research Report**  
Once it has enough data, it:  
- Generates a final research document, summarizing all relevant findings.  
- Outputs a clean, structured, and formatted report.

---

## 🛠️ Tech Stack & Dependencies

- 🔹 **Programming Language**: Python 3.9+  
- 🔹 **Core APIs**:  
  - 🔥 [FireCrawl Batch Scrape API](https://firecrawl.ai) – Web scraping & data extraction.  
  - 🧠 [OpenRouter API](https://openrouter.ai) – Query generation & summarization via LLMs.  
- 🔹 **Asynchronous Networking**: `aiohttp` for non-blocking API calls.  
- 🔹 **Data Processing**: `json`, `pydantic` for structured data extraction.  
- 🔹 **Web Scraping Backup**: `BeautifulSoup4` (for manual HTML parsing).  

### 📦 Key Python Packages:
```bash
firecrawl-py
aiohttp
pydantic
python-dotenv
beautifulsoup4
```

---
## 📌 Why FireCrawl Instead of Jina?
- 🔥 FireCrawl = CHEAPER (Jina is expensive & mid).
- 🚀 Faster Batch Scraping (Jina was slow as hell).
- 💾 Structured Data Extraction (Jina didn’t support full-schema extraction).
---
## 🤖 The Name: Why IrisLens?
- "Iris" = The eye, seeing through the noise of web search.
- "Lens" = Focus, filtering the right research for you.
It’s basically an "AI microscope for the internet."
---
## 🚀 What’s Next?
- 🔗 Direct PDF/Doc Generation – Export research as clean PDFs.
- 🛜 Live Webpage Monitoring – Continuously update reports when new sources appear.
- 📊 AI-Assisted Trend Analysis – Detect shifts in web opinions.
---
## 💡 Final Thoughts
IrisLens isn’t the best, but it’s good enough for now. It’s basically DeepResearch's drunk cousin, but hey, it works. 🎯
🛠️ Made with sweat & Python.
🐍 Hack away & improve it!
