import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Home from './pages/Home';
import Architecture from './pages/Architecture';
import Research from './pages/Research';
import Demo from './pages/Demo';
import Docs from './pages/Docs';
import Footer from './components/Footer';
import './index.css';

export default function App() {
  return (
    <BrowserRouter>
      <header className="p-4 bg-gray-800 text-white flex justify-between">
        <div className="font-bold">AGI-SAC</div>
        <nav className="space-x-4">
          <Link to="/">Home</Link>
          <Link to="/architecture">Architecture</Link>
          <Link to="/research">Research</Link>
          <Link to="/demo">Demo</Link>
          <Link to="/docs">Docs</Link>
        </nav>
      </header>
      <main className="min-h-screen">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/architecture" element={<Architecture />} />
          <Route path="/research" element={<Research />} />
          <Route path="/demo" element={<Demo />} />
          <Route path="/docs" element={<Docs />} />
        </Routes>
      </main>
      <Footer />
    </BrowserRouter>
  );
}
