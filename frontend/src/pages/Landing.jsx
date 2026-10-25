import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Plane, Sparkles, Route, Wallet, Clock, ArrowRight } from 'lucide-react'
import { isLoggedIn } from '../utils/auth'

const features = [
  { icon: Sparkles, title: 'AI-Powered Planning', text: 'Personalized itineraries generated instantly using advanced AI models tailored to your taste.' },
  { icon: Route, title: 'Smart Route Optimization', text: 'Minimize travel time and maximize experiences with algorithmically optimized paths.' },
  { icon: Wallet, title: 'Budget-Conscious', text: 'Stay within your budget with real-time INR cost estimations and smart recommendations.' },
  { icon: Clock, title: 'Time Management', text: 'Perfect pacing for your travel style — choose between relaxed, moderate, or fast tracks.' },
]

const testimonials = [
  { quote: 'Finally, a travel tool that feels like it belongs in 2026. The AI itinerary was spot on and saved me hours.', name: 'Sarah Jenkins', role: 'Digital Nomad' },
  { quote: 'The route optimization is real. I saw more of Tokyo in 3 days than I did in a week last time.', name: 'Michael Chen', role: 'Frequent Flyer' },
  { quote: 'Clean, fast, and beautiful. It\'s the Notion of travel planning. I recommend it to all my readers.', name: 'Elena Rodriguez', role: 'Adventure Blogger' },
]

export const Landing = () => {
  const navigate = useNavigate()
  const go = () => navigate(isLoggedIn() ? '/dashboard' : '/register')
  return (
    <div style={{ background: 'linear-gradient(180deg,#f8fafc 0%,#ffffff 40%)' }}>
      <div className="container">
        <div className="landing-nav">
          <div className="brand" style={{ padding: 0 }}>
            <div className="brand-mark"><Plane size={16} /></div>Travel<span>Planner</span>
          </div>
          <nav>
            <a href="#features">Features</a>
            <a href="#how">How it works</a>
            <a href="#testimonials">Testimonials</a>
          </nav>
          <div className="row">
            <Link to="/login" className="btn btn-ghost btn-sm">Sign in</Link>
            <button className="btn btn-primary btn-sm" onClick={go}>Get Started</button>
          </div>
        </div>

        <section className="hero">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <div className="eyebrow row" style={{ gap: 6, marginBottom: 16 }}><Sparkles size={12} /> AI-powered travel OS</div>
            <h1>Plan your next <em>adventure</em> in seconds.</h1>
            <p>The most advanced AI travel companion that handles the complexity of planning so you can focus on the experience.</p>
            <div className="row" style={{ marginTop: 26 }}>
              <button className="btn btn-primary btn-lg" onClick={go}>Start Planning Free <ArrowRight size={16} /></button>
              <span className="muted" style={{ fontSize: 13 }}>★★★★★ 2,000+ travellers</span>
            </div>
          </motion.div>
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.6, delay: 0.1 }}>
            <div className="mock">
              <div className="row between"><div className="line" style={{ width: 120 }} /><span className="badge badge-blue">Goa, India</span></div>
              <div className="grid grid-3" style={{ gap: 10, margin: '14px 0' }}>
                {[1, 2, 3].map((i) => <div key={i} className="card card-pad" style={{ padding: 12 }}><div className="line" style={{ width: '60%' }} /><div className="line" /></div>)}
              </div>
              <div className="card card-pad" style={{ padding: 14 }}>
                <div className="eyebrow">Day 1 · Morning</div>
                <div className="line" style={{ width: '85%' }} /><div className="line" style={{ width: '70%' }} />
                <div className="row between" style={{ marginTop: 8 }}><div className="line" style={{ width: 80, margin: 0 }} /><b style={{ color: 'var(--primary)' }}>₹2,100 / day</b></div>
              </div>
            </div>
          </motion.div>
        </section>

        <section className="section" id="features">
          <h2>Built for the modern traveler</h2>
          <p className="sub">Everything you need to organize your journey, all in one premium interface.</p>
          <div className="grid grid-4">
            {features.map(({ icon: Icon, title, text }) => (
              <motion.div key={title} className="card feature" whileHover={{ y: -4 }}>
                <div className="ic"><Icon size={18} /></div>
                <h4>{title}</h4>
                <p>{text}</p>
              </motion.div>
            ))}
          </div>
        </section>

        <section className="section" id="how" style={{ paddingTop: 0 }}>
          <div className="card card-pad row between wrap" style={{ gap: 30 }}>
            <div>
              <h3 style={{ fontSize: 24 }}>Enterprise-grade reliability</h3>
              <p className="muted" style={{ margin: '6px 0 0', maxWidth: 360 }}>We use the same technology powering top logistics firms to ensure your trip is perfectly optimized.</p>
            </div>
            <div className="logos"><span>AIRBNB</span><span>EXPEDIA</span><span>TRIPADVISOR</span><span>BOOKING</span></div>
          </div>
        </section>

        <section className="section" id="testimonials" style={{ paddingTop: 0 }}>
          <div className="grid grid-3">
            {testimonials.map((t) => (
              <div key={t.name} className="card testi">
                <div className="stars">★★★★★</div>
                <p style={{ lineHeight: 1.6, color: '#334155' }}>“{t.quote}”</p>
                <div className="row"><div className="avatar" style={{ background: '#e2e8f0', color: '#475569' }}>{t.name[0]}</div><div><b style={{ fontSize: 14 }}>{t.name}</b><br /><small className="muted" style={{ letterSpacing: '.08em', textTransform: 'uppercase', fontSize: 10 }}>{t.role}</small></div></div>
              </div>
            ))}
          </div>
        </section>

        <section className="section" style={{ paddingTop: 0 }}>
          <div className="cta">
            <h2>Your next story starts here.</h2>
            <p style={{ opacity: 0.8, margin: '12px 0 26px' }}>Join 10,000+ travelers planning their dream trips today.</p>
            <button className="btn btn-lg" style={{ background: '#60a5fa', color: '#0f172a' }} onClick={go}>Create My Itinerary</button>
          </div>
        </section>
        <footer>© {new Date().getFullYear()} TravelPlanner · Built with React, FastAPI & Supabase</footer>
      </div>
    </div>
  )
}

export default Landing
