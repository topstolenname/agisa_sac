import TrustGraph from '../components/TrustGraph';
import AgentVisualizer from '../components/AgentVisualizer';

export default function Architecture() {
  return (
    <div className="p-4 space-y-4">
      <TrustGraph />
      <AgentVisualizer />
    </div>
  );
}
