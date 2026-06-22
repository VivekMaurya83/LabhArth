/**
 * Search — Scheme search page.
 *
 * Search bar with filters and results displayed as SchemeCards.
 */

import { useState } from 'react';
import SchemeCard from '../components/SchemeCard';
import { searchSchemes } from '../services/api';
import './Search.css';

export default function Search() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setSearched(true);
    try {
      const data = await searchSchemes(query);
      setResults(data.results || []);
    } catch (err) {
      console.error('Search failed:', err);
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="search-page" id="page-search">
      <h1 className="search-title">Search Government Schemes</h1>
      <p className="search-subtitle">
        Find welfare schemes using natural language — try "scholarships for SC students in Maharashtra"
      </p>

      <form className="search-form" onSubmit={handleSearch}>
        <input
          type="text"
          className="search-input"
          id="search-input"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="What scheme are you looking for?"
          autoFocus
        />
        <button type="submit" className="search-btn" id="search-submit" disabled={isLoading}>
          {isLoading ? 'Searching...' : 'Search'}
        </button>
      </form>

      <div className="search-results">
        {isLoading && <div className="search-loading">Searching schemes...</div>}
        {!isLoading && searched && results.length === 0 && (
          <div className="search-empty">
            No schemes found. Try a different query or check back when the database is populated.
          </div>
        )}
        {results.map((scheme) => (
          <SchemeCard key={scheme.id} scheme={scheme} />
        ))}
      </div>
    </div>
  );
}
