import { Link, useNavigate } from 'react-router-dom';
import { useState, useEffect, useRef } from 'react';
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
 * PromptCardWithTilt — Interactive helper card with 3D perspective hover tilt.
 */
function PromptCard({ title, text, icon: IconComp, onClick }) {
  const [tilt, setTilt] = useState({ x: 0, y: 0 });

  const handleMouseMove = (e) => {
    const card = e.currentTarget;
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const xc = rect.width / 2;
    const yc = rect.height / 2;
    
    const maxTilt = 8;
    const tiltX = -((y - yc) / yc) * maxTilt;
    const tiltY = ((x - xc) / xc) * maxTilt;
    
    setTilt({ x: tiltX, y: tiltY });
  };

  const handleMouseLeave = () => {
    setTilt({ x: 0, y: 0 });
  };

  return (
    <motion.div 
      className="prompt-card" 
      onClick={onClick}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{
        transform: `perspective(1000px) rotateX(${tilt.x}deg) rotateY(${tilt.y}deg)`,
        transition: 'transform 0.1s ease-out, box-shadow var(--transition-fast)',
      }}
    >
      <div className="prompt-card-header-icon">
        <IconComp size={20} className="prompt-icon" />
      </div>
      <h4>{title}</h4>
      <p className="prompt-card-text">"{text}"</p>
      <span className="prompt-card-action">
        <span>Ask AI</span>
        <ArrowRight size={14} />
      </span>
    </motion.div>
  );
}

/**
 * Home — Landing page view with interactive canvas particles, spring title renders,
 * and 3D card tilt effects.
 */
export default function Home() {
  const navigate = useNavigate();
  const canvasRef = useRef(null);

  const handleQuickChat = (promptText) => {
    navigate('/chat', { state: { presetPrompt: promptText } });
  };

  const handleQuickSearch = (categoryKey) => {
    navigate('/search', { state: { presetCategory: categoryKey } });
  };

  // Typographic animation variants
  const sentenceVariants = {
    hidden: { opacity: 1 },
    visible: {
      opacity: 1,
      transition: {
        delay: 0.1,
        staggerChildren: 0.02,
      }
    }
  };

  const letterVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { type: 'spring', damping: 12, stiffness: 120 }
    }
  };

  // Canvas particle network setup
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    let width = (canvas.width = canvas.offsetWidth);
    let height = (canvas.height = canvas.offsetHeight);

    const particles = [];
    const particleCount = Math.min(50, Math.floor((width * height) / 18000));
    const connectionDistance = 100;
    const mouse = { x: null, y: null, radius: 120 };

    class Particle {
      constructor() {
        this.x = Math.random() * width;
        this.y = Math.random() * height;
        this.vx = (Math.random() - 0.5) * 0.35;
        this.vy = (Math.random() - 0.5) * 0.35;
        this.radius = Math.random() * 2 + 1;
      }

      update() {
        this.x += this.vx;
        this.y += this.vy;

        if (this.x < 0 || this.x > width) this.vx *= -1;
        if (this.y < 0 || this.y > height) this.vy *= -1;

        if (mouse.x !== null && mouse.y !== null) {
          const dx = this.x - mouse.x;
          const dy = this.y - mouse.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < mouse.radius) {
            const force = (mouse.radius - dist) / mouse.radius;
            const angle = Math.atan2(dy, dx);
            this.x += Math.cos(angle) * force * 1.2;
            this.y += Math.sin(angle) * force * 1.2;
          }
        }
      }

      draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(79, 70, 229, 0.25)';
        ctx.fill();
      }
    }

    for (let i = 0; i < particleCount; i++) {
      particles.push(new Particle());
    }

    const handleMouseMove = (e) => {
      const rect = canvas.getBoundingClientRect();
      mouse.x = e.clientX - rect.left;
      mouse.y = e.clientY - rect.top;
    };

    const handleMouseLeave = () => {
      mouse.x = null;
      mouse.y = null;
    };

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = canvas.offsetWidth;
      height = canvas.height = canvas.offsetHeight;
    };

    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseleave', handleMouseLeave);
    window.addEventListener('resize', handleResize);

    const animate = () => {
      ctx.clearRect(0, 0, width, height);

      // Draw network connections
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < connectionDistance) {
            const alpha = (1 - dist / connectionDistance) * 0.15;
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.strokeStyle = `rgba(16, 185, 129, ${alpha})`;
            ctx.lineWidth = 0.8;
            ctx.stroke();
          }
        }
      }

      particles.forEach((p) => {
        p.update();
        p.draw();
      });

      animationFrameId = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      cancelAnimationFrame(animationFrameId);
      if (canvas) {
        canvas.removeEventListener('mousemove', handleMouseMove);
        canvas.removeEventListener('mouseleave', handleMouseLeave);
      }
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  // Split sentence into words, and words into characters to prevent word breaks
  const splitText = (text) => {
    const words = text.split(' ');
    return words.map((word, wordIdx) => {
      return (
        <span 
          key={wordIdx} 
          style={{ display: 'inline-block', whiteSpace: 'nowrap' }}
        >
          {word.split('').map((char, charIdx) => (
            <motion.span 
              key={charIdx} 
              variants={letterVariants}
              style={{ display: 'inline-block' }}
            >
              {char}
            </motion.span>
          ))}
          {/* Add trailing space after word container (except final item) */}
          {wordIdx < words.length - 1 && (
            <motion.span 
              variants={letterVariants}
              style={{ display: 'inline-block' }}
            >
              {'\u00A0'}
            </motion.span>
          )}
        </span>
      );
    });
  };

  return (
    <motion.div 
      className="home" 
      id="page-home"
      initial="hidden"
      animate="visible"
      variants={{
        hidden: { opacity: 0 },
        visible: {
          opacity: 1,
          transition: { staggerChildren: 0.1, delayChildren: 0.05 }
        }
      }}
    >
      {/* Hero Section */}
      <motion.section className="hero" variants={{ hidden: { opacity: 0, y: 15 }, visible: { opacity: 1, y: 0 } }}>
        {/* Interactive network canvas layer */}
        <canvas ref={canvasRef} className="hero-canvas" />

        {/* Decorative background shapes */}
        <div className="hero-decorations" aria-hidden="true">
          <div className="decor-shape decor-shape--1"></div>
          <div className="decor-shape decor-shape--2"></div>
        </div>

        <div className="hero-badge">
          <svg className="hero-badge-logo" width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 6H20" stroke="var(--color-accent)" strokeWidth="4" strokeLinecap="round"/>
            <circle cx="12" cy="12" r="3.5" stroke="var(--color-primary)" strokeWidth="2.5"/>
            <path d="M4 18H20" stroke="var(--color-secondary)" strokeWidth="4" strokeLinecap="round"/>
          </svg>
          <span>AI-Powered Government Welfare Discovery</span>
        </div>
        
        {/* Character-level sequential typographic reveal header */}
        <motion.h1 
          className="hero-title"
          variants={sentenceVariants}
          initial="hidden"
          animate="visible"
        >
          {splitText("Discover ")}
          <span className="gradient-text">{splitText("Government Schemes")}</span>
          {splitText(" You Qualify For")}
        </motion.h1>
        
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

      {/* Suggested Quick Categories */}
      <motion.section 
        className="home-suggestions" 
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-60px" }}
        transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      >
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
                whileHover={{ scale: 1.04, y: -2 }}
                whileTap={{ scale: 0.98 }}
              >
                <IconComp size={14} className="tag-icon" />
                <span>{cat.label}</span>
              </motion.button>
            );
          })}
        </div>
      </motion.section>

      {/* Prompt suggestions with 3D Tilt */}
      <motion.section 
        className="home-prompts" 
        initial={{ opacity: 0, y: 35 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-80px" }}
        transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      >
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
          ].map((prompt, idx) => (
            <PromptCard
              key={idx}
              title={prompt.title}
              text={prompt.text}
              icon={prompt.icon}
              onClick={() => handleQuickChat(prompt.prompt)}
            />
          ))}
        </div>
      </motion.section>

      {/* Value Propositions with Staggered Scroll-Reveal */}
      <motion.section 
        className="features"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-100px" }}
        variants={{
          hidden: { opacity: 0 },
          visible: {
            opacity: 1,
            transition: {
              staggerChildren: 0.15
            }
          }
        }}
      >
        <motion.div 
          className="feature-card" 
          id="feature-discover" 
          whileHover={{ y: -3 }}
          variants={{
            hidden: { opacity: 0, y: 30 },
            visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] } }
          }}
        >
          <div className="feature-icon-wrapper">
            <Zap size={22} className="feature-icon" />
          </div>
          <h3>AI-Powered Retrieval</h3>
          <p>Semantic search matches natural statements with contextual scheme contents, going beyond simple keyword filters.</p>
        </motion.div>
        
        <motion.div 
          className="feature-card" 
          id="feature-eligibility" 
          whileHover={{ y: -3 }}
          variants={{
            hidden: { opacity: 0, y: 30 },
            visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] } }
          }}
        >
          <div className="feature-icon-wrapper">
            <ShieldCheck size={22} className="feature-icon" />
          </div>
          <h3>Rule Evaluation</h3>
          <p>Instantly verifies your profiles against eligibility requirements, listing missing conditions and clear reasoning.</p>
        </motion.div>
        
        <motion.div 
          className="feature-card" 
          id="feature-guidance" 
          whileHover={{ y: -3 }}
          variants={{
            hidden: { opacity: 0, y: 30 },
            visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] } }
          }}
        >
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
