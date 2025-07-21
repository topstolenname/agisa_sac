import TrustGraph from '../components/TrustGraph';
import AgentVisualizer from '../components/AgentVisualizer';
import MetricCards from '../components/MetricCards';

export default function Architecture() {
  return (
    <div className="p-4 space-y-4">
      <MetricCards />
      <TrustGraph />
      <AgentVisualizer />
    </div>
  );
}
