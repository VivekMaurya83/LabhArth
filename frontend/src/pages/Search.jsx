import { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Search as SearchIcon, ShieldCheck, FileText, RefreshCw, Filter } from 'lucide-react';
import SchemeCard from '../components/SchemeCard';
import EligibilityForm from '../components/EligibilityForm';
import EligibilityBadge from '../components/EligibilityBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorBanner from '../components/ErrorBanner';
import { searchSchemes, evaluateBulkEligibility } from '../services/api';
import './Search.css';

const CANONICAL_CATEGORIES = [
  { key: 'education', label: 'Education & Scholarships' },
  { key: 'agriculture', label: 'Agriculture & Farmer Subsidies' },
  { key: 'health', label: 'Health & Medical Support' },
  { key: 'housing', label: 'Housing & Shelter' },
  { key: 'social_welfare', label: 'Social Welfare & Pensions' },
  { key: 'employment', label: 'Employment & Skill Development' },
  { key: 'women_children', label: 'Women & Child Welfare' },
  { key: 'minority', label: 'Minority Welfare' },
  { key: 'disability', label: 'Disability Support' },
  { key: 'financial_inclusion', label: 'Financial Inclusion & Banking' },
  { key: 'other', label: 'Other Welfare Services' }
];

const STATES = [
  'Maharashtra',
  'Karnataka',
  'Gujarat',
  'Delhi',
  'Uttar Pradesh',
  'Madhya Pradesh',
  'Tamil Nadu',
  'Rajasthan',
  'Bihar',
  'West Bengal'
];

/**
 * Search — Scheme catalog search view.
 *
 * Employs responsive grids, animated list entries, and slide-in sidebars.
 */
export default function Search() {
  const location = useLocation();
  const navigateInitialized = useRef(false);

  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');
  const [stateFilter, setStateFilter] = useState('');
  
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState(null);

  // Eligibility evaluation states
  const [showEligibilityForm, setShowEligibilityForm] = useState(false);
  const [eligibilityResults, setEligibilityResults] = useState({});
  const [isCheckingEligibility, setIsCheckingEligibility] = useState(false);
  const [eligibilityError, setEligibilityError] = useState(null);

  // Auto-run search when redirected from Home page suggestions
  useEffect(() => {
    if (!navigateInitialized.current && location.state) {
      navigateInitialized.current = true;
      if (location.state.presetCategory) {
        setCategory(location.state.presetCategory);
        executeSearch('', { category: location.state.presetCategory });
      }
    }
  }, [location]);

  const executeSearch = async (searchQuery, filters = {}) => {
    setIsLoading(true);
    setSearched(true);
    setError(null);
    setEligibilityResults({}); // Reset prior check matches
    
    try {
      const activeFilters = {
        category: filters.hasOwnProperty('category') ? filters.category : category,
        state: filters.hasOwnProperty('state') ? filters.state : stateFilter,
      };

      const data = await searchSchemes(searchQuery, activeFilters);
      setResults(data.results || []);
    } catch (err) {
      console.error('Search failed:', err);
      setError(err.message || 'An error occurred while fetching schemes. Ensure backend is running.');
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    executeSearch(query);
  };

  const handleFilterChange = (filterType, val) => {
    if (filterType === 'category') {
      setCategory(val);
    } else if (filterType === 'state') {
      setStateFilter(val);
    }
  };

  const handleClearFilters = () => {
    setQuery('');
    setCategory('');
    setStateFilter('');
    setResults([]);
    setSearched(false);
    setError(null);
    setEligibilityResults({});
    setShowEligibilityForm(false);
  };

  const handleCheckEligibility = async (profileData) => {
    setIsCheckingEligibility(true);
    setEligibilityError(null);
    try {
      const evalData = await evaluateBulkEligibility(profileData);
      
      const resultMap = {};
      evalData.forEach((item) => {
        resultMap[item.scheme_id] = item;
      });
      setEligibilityResults(resultMap);
    } catch (err) {
      console.error('Bulk eligibility check failed:', err);
      setEligibilityError(err.message || 'Failed to check eligibility. Verify profile inputs.');
    } finally {
      setIsCheckingEligibility(false);
    }
  };

  return (
    <div className="search-page" id="page-search">
      <div className="search-header-container">
        <h1 className="search-title">Welfare Scheme Catalog</h1>
        <p className="search-subtitle">
          Search for government initiatives using natural keywords and filter by state or category.
        </p>
      </div>

      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

      <form className="search-form" onSubmit={handleSearch}>
        <div className="search-bar-row">
          <div className="search-input-wrapper">
            <SearchIcon size={18} className="search-bar-icon" />
            <input
              type="text"
              className="search-input"
              id="search-input"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Type keywords (e.g. 'education scholarships', 'farmer loans'...)"
              autoFocus
            />
          </div>
          <button type="submit" className="search-btn" id="search-submit" disabled={isLoading}>
            <span>{isLoading ? 'Searching...' : 'Search'}</span>
          </button>
        </div>

        {/* Filters Panel */}
        <div className="search-filters">
          <div className="filter-group">
            <label htmlFor="category-select">
              <Filter size={12} className="label-icon" />
              <span>Category</span>
            </label>
            <select
              id="category-select"
              value={category}
              onChange={(e) => handleFilterChange('category', e.target.value)}
            >
              <option value="">All Categories</option>
              {CANONICAL_CATEGORIES.map((cat) => (
                <option key={cat.key} value={cat.key}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="state-select">
              <Filter size={12} className="label-icon" />
              <span>State / Level</span>
            </label>
            <select
              id="state-select"
              value={stateFilter}
              onChange={(e) => handleFilterChange('state', e.target.value)}
            >
              <option value="">All States / Central</option>
              <option value="Central">Central (National)</option>
              {STATES.map((st) => (
                <option key={st} value={st}>
                  {st}
                </option>
              ))}
            </select>
          </div>

          {(query || category || stateFilter) && (
            <motion.button 
              type="button" 
              className="clear-filters-btn" 
              onClick={handleClearFilters}
              whileHover={{ rotate: 15 }}
              whileTap={{ scale: 0.95 }}
            >
              <RefreshCw size={12} />
              <span>Reset All</span>
            </motion.button>
          )}
        </div>
      </form>

      {/* Main Results Layout */}
      <div className="search-layout">
        {/* Results Listings */}
        <div className="search-listings-container">
          {isLoading && <LoadingSpinner message="Retrieving schemes from knowledge base..." />}

          {!isLoading && searched && results.length === 0 && (
            <div className="search-empty">
              <h3>No schemes matched your criteria</h3>
              <p>Try refining your query, choosing another state, or selecting "All Categories".</p>
            </div>
          )}

          {!isLoading && results.length > 0 && (
            <div className="search-results-list">
              <div className="results-header-row">
                <span className="results-count">Found {results.length} matching schemes</span>
                
                {/* Toggle Bulk Check */}
                <button
                  type="button"
                  className={`toggle-check-btn ${showEligibilityForm ? 'active' : ''}`}
                  onClick={() => setShowEligibilityForm(!showEligibilityForm)}
                >
                  <ShieldCheck size={14} className="toggle-btn-icon" />
                  <span>{showEligibilityForm ? 'Hide Profile Checker' : 'Verify Eligibility Across Results'}</span>
                </button>
              </div>

              <motion.div 
                className="results-grid-container"
                initial="hidden"
                animate="visible"
                variants={{
                  hidden: { opacity: 0 },
                  visible: {
                    opacity: 1,
                    transition: { staggerChildren: 0.08 }
                  }
                }}
              >
                {results.map((scheme) => {
                  const evalData = eligibilityResults[scheme.id];

                  return (
                    <motion.div 
                      key={scheme.id} 
                      className="scheme-card-wrapper"
                      variants={{
                        hidden: { opacity: 0, y: 12 },
                        visible: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } }
                      }}
                    >
                      <SchemeCard scheme={scheme} eligibility={evalData} />
                      
                      {/* Embedded Eligibility Report if checked */}
                      {evalData && (
                        <div className="scheme-card-eval-report">
                          <div className="eval-report-header">
                            <span className="eval-report-label">Your Evaluation:</span>
                            <EligibilityBadge 
                              eligible={
                                evalData.is_eligible 
                                  ? 'eligible' 
                                  : evalData.missing_criteria && evalData.missing_criteria.length > 5
                                    ? 'not eligible'
                                    : 'partially eligible'
                              } 
                            />
                          </div>
                          <p className="eval-report-reasoning">
                            <strong>Details:</strong> {evalData.reasoning}
                          </p>
                          {evalData.missing_criteria && evalData.missing_criteria.length > 0 && (
                            <div className="eval-report-missing">
                              <strong>Unresolved / Missing Criteria:</strong>
                              <ul>
                                {evalData.missing_criteria.map((crit, index) => (
                                  <li key={index}>{crit}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {evalData.is_eligible && evalData.required_documents && evalData.required_documents.length > 0 && (
                            <div className="eval-report-docs">
                              <strong>Required Documents:</strong>
                              <div className="docs-badge-row">
                                {evalData.required_documents.map((doc, idx) => (
                                  <span key={idx} className="doc-mini-badge">
                                    <FileText size={11} className="doc-mini-icon" />
                                    <span>{doc}</span>
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </motion.div>
                  );
                })}
              </motion.div>
            </div>
          )}
        </div>

        {/* Sidebar Profile Form */}
        <AnimatePresence>
          {showEligibilityForm && results.length > 0 && (
            <motion.div 
              className="search-sidebar-checker"
              initial={{ opacity: 0, x: 25 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 25 }}
              transition={{ duration: 0.25, ease: 'easeOut' }}
            >
              {eligibilityError && <ErrorBanner message={eligibilityError} onDismiss={() => setEligibilityError(null)} />}
              <EligibilityForm onSubmit={handleCheckEligibility} isLoading={isCheckingEligibility} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
