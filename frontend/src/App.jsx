import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/Home';
import Search from './pages/Search';
import SchemeDetails from './pages/SchemeDetails';
import Chat from './pages/Chat';
import './App.css';

/**
 * LabhArth AI — Root Application Component
 *
 * Defines the app layout and page routing.
 */
function App() {
  return (
    <div className="app">
      <Navbar />
      <main className="app-main">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/search" element={<Search />} />
          <Route path="/scheme/:id" element={<SchemeDetails />} />
          <Route path="/chat" element={<Chat />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

export default App;
