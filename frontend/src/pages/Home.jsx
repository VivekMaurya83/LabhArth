import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  MessageSquare, 
  Search, 
  GraduationCap, 
  Sprout, 
  Heart, 
  Home as HomeIcon, 
  Coins, 
  Accessibility, 
  ArrowRight,
  Zap,
  ShieldCheck,
  FileText
} from 'lucide-react';
import './Home.css';

/**
 * Home — Landing page view with interactive motions, system summaries,
 * and quick presets for RAG searches and chat consultations.
 */
export default function Home() {
  const navigate = useNavigate();

  const handleQuickChat = (promptText) => {
    navigate('/chat', { state: { presetPrompt: promptText } });
  };

  const handleQuickSearch = (categoryKey) => {
    navigate('/search', { state: { presetCategory: categoryKey } });
  };

  // Framer Motion animation presets
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.05
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 15 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.4, ease: 'easeOut' }
    }
  };

  return (
    <motion.div 
      className="home" 
      id="page-home"
      initial="hidden"
      animate="visible"
      variants={containerVariants}
    >
      {/* Hero Section */}
      <motion.section className="hero" variants={itemVariants}>
        {/* Floating background shapes with CSS animation */}
        <div className="hero-decorations" aria-hidden="true">
          <div className="decor-shape decor-shape--1"></div>
          <div className="decor-shape decor-shape--2"></div>
        </div>

        <div className="hero-badge">
          {/* Chakra vector badge icon */}
          <svg className="hero-badge-logo" width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 6H20" stroke="var(--color-accent)" strokeWidth="4" strokeLinecap="round"/>
            <circle cx="12" cy="12" r="3.5" stroke="var(--color-primary)" strokeWidth="2.5"/>
            <path d="M4 18H20" stroke="var(--color-secondary)" strokeWidth="4" strokeLinecap="round"/>
          </svg>
          <span>AI-Powered Government Welfare Discovery</span>
        </div>
        
        <h1 className="hero-title">
          Discover <span className="gradient-text">Government Schemes</span> You Qualify For
        </h1>
        
        <p className="hero-subtitle">
          LabhArth AI uses Multi-Agent systems and Semantic RAG to connect Indian citizens
          with relevant welfare opportunities, evaluate eligibility rules, and guide application processes.
        </p>
        
        <div className="hero-actions">
          <Link to="/chat" className="btn btn-primary" id="cta-chat">
            <MessageSquare size={16} />
            <span>Consult Welfare Assistant</span>
          </Link>
          <Link to="/search" className="btn btn-secondary" id="cta-search">
            <Search size={16} />
            <span>Browse & Filter Schemes</span>
          </Link>
        </div>
      </motion.section>

      {/* Suggested Quick Search Categories */}
      <motion.section className="home-suggestions" variants={itemVariants}>
        <h3 className="suggestions-title">Quick Search by Category</h3>
        <div className="category-tags">
          {[
            { key: 'education', icon: GraduationCap, label: 'Education & Scholarships' },
            { key: 'agriculture', icon: Sprout, label: 'Agriculture & Farmer Subsidies' },
            { key: 'women_children', icon: Heart, label: 'Women & Child Welfare' },
            { key: 'housing', icon: HomeIcon, label: 'Housing & Shelter' },
            { key: 'financial_inclusion', icon: Coins, label: 'Financial Inclusion' },
            { key: 'disability', icon: Accessibility, label: 'Disability Support' }
          ].map((cat) => {
            const IconComp = cat.icon;
            return (
              <motion.button 
                key={cat.key}
                type="button" 
                className="tag-btn" 
                onClick={() => handleQuickSearch(cat.key)}
                whileHover={{ scale: 1.03, y: -1 }}
                whileTap={{ scale: 0.98 }}
              >
                <IconComp size={14} className="tag-icon" />
                <span>{cat.label}</span>
              </motion.button>
            );
          })}
        </div>
      </motion.section>

      {/* Prompt Suggestions */}
      <motion.section className="home-prompts" variants={itemVariants}>
        <h3 className="prompts-title">Ask the Assistant</h3>
        <div className="prompt-cards">
          {[
            {
              title: 'Student Scholarship',
              text: 'Which scholarships are available for female students in Maharashtra with family income under ₹2 Lakh?',
              icon: GraduationCap,
              prompt: 'Which scholarships are available for female students in Maharashtra with family income under ₹2 Lakh?'
            },
            {
              title: 'Women & Widow Support',
              text: 'Welfare schemes and pensions available for widows and unemployed women in Jammu & Kashmir.',
              icon: Heart,
              prompt: 'Welfare schemes and pensions available for widows and unemployed women in Jammu & Kashmir.'
            },
            {
              title: 'Farmer Subsidies',
              text: 'Are there any seed, fertilizer, or agricultural machinery subsidies for small farmers in Rajasthan?',
              icon: Sprout,
              prompt: 'Are there any seed, fertilizer, or agricultural machinery subsidies for small farmers in Rajasthan?'
            }
          ].map((prompt, idx) => {
            const IconComp = prompt.icon;
            return (
              <motion.div 
                key={idx}
                className="prompt-card" 
                onClick={() => handleQuickChat(prompt.prompt)}
                whileHover={{ y: -4, scale: 1.015 }}
                transition={{ type: 'spring', stiffness: 300, damping: 20 }}
              >
                <div className="prompt-card-header-icon">
                  <IconComp size={20} className="prompt-icon" />
                </div>
                <h4>{prompt.title}</h4>
                <p className="prompt-card-text">"{prompt.text}"</p>
                <span className="prompt-card-action">
                  <span>Ask AI</span>
                  <ArrowRight size={14} />
                </span>
              </motion.div>
            );
          })}
        </div>
      </motion.section>

      {/* Value Propositions */}
      <motion.section className="features" variants={itemVariants}>
        <motion.div className="feature-card" id="feature-discover" whileHover={{ y: -2 }}>
          <div className="feature-icon-wrapper">
            <Zap size={22} className="feature-icon" />
          </div>
          <h3>AI-Powered Retrieval</h3>
          <p>Semantic search matches natural statements with contextual scheme contents, going beyond simple keyword filters.</p>
        </motion.div>
        
        <motion.div className="feature-card" id="feature-eligibility" whileHover={{ y: -2 }}>
          <div className="feature-icon-wrapper">
            <ShieldCheck size={22} className="feature-icon" />
          </div>
          <h3>Rule Evaluation</h3>
          <p>Instantly verifies your profiles against eligibility requirements, listing missing conditions and clear reasoning.</p>
        </motion.div>
        
        <motion.div className="feature-card" id="feature-guidance" whileHover={{ y: -2 }}>
          <div className="feature-icon-wrapper">
            <FileText size={22} className="feature-icon" />
          </div>
          <h3>Document Guide</h3>
          <p>Extracts required papers, mandatory proofs, and acceptable alternatives to accelerate preparation.</p>
        </motion.div>
      </motion.section>
    </motion.div>
  );
}
