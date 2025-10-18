import { Routes, Route, Link } from 'react-router-dom';
import Home from './pages/Home';
import Architecture from './pages/Architecture';
import Research from './pages/Research';
import Demo from './pages/Demo';
import Docs from './pages/Docs';
import Footer from './components/Footer';

const pages = [
  { path: '/', name: 'Home', Component: Home },
  { path: '/architecture', name: 'Architecture', Component: Architecture },
  { path: '/research', name: 'Research', Component: Research },
  { path: '/demo', name: 'Demo', Component: Demo },
  { path: '/docs', name: 'Docs', Component: Docs },
];

export default function App() {
  return (
    <>
      <header className="p-4 bg-gray-800 text-white flex justify-between">
        <div className="font-bold">AGI-SAC</div>
        <nav className="space-x-4">
          {pages.map(({ path, name }) => (
            <Link key={path} to={path}>
              {name}
            </Link>
          ))}
        </nav>
      </header>
      <main className="min-h-screen">
        <Routes>
          {pages.map(({ path, Component }) => (
            <Route key={path} path={path} element={<Component />} />
          ))}
        </Routes>
      </main>
      <Footer />
    </>
  );
}
