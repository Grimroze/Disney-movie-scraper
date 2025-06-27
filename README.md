# Disney-movie-scraper
# 🎬 Disney Movie Scraper & Analyzer

This project scrapes a list of Walt Disney Pictures films from Wikipedia, cleans and enriches the data, and exports it for further analysis.

It includes:
- Web scraping with BeautifulSoup
- Parsing infobox fields like budget, box office, release dates, running time
- Currency and time conversions
- Metadata enrichment using the OMDb API (IMDb rating, Metascore, Rotten Tomatoes, etc.)
- Data export to JSON and Pickle
- Optional: Save cleaned data to Pandas DataFrame for analysis

---

## 📊 Features

- ✅ Scrapes all Disney films from the [Wikipedia master list](https://en.wikipedia.org/wiki/List_of_Walt_Disney_Pictures_films)
- ✅ Converts budget and box office from `string numbers` to actual USD integers
- ✅ Extracts and formats release dates as `datetime` objects
- ✅ Uses [OMDb API](https://www.omdbapi.com/) to fetch:
  - IMDb rating
  - Metascore
  - Rotten Tomatoes score
  - Genre, plot, votes, awards & more
- ✅ Saves final cleaned data to:
  - `Disney_data_final.pkl` (Pickle)
  - `movies_data.json` (JSON)
  - Ready-to-use Pandas DataFrame

---

## 🚀 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Grimroze/disney-movie-scraper.git
cd disney-movie-scraper
