export default function MetricCards() {
  const metrics = [
    { name: 'Coherence Index', value: '87%' },
    { name: 'Trust Volatility', value: '12%' },
    { name: 'Emergence Score', value: '0.78' },
    { name: 'Active Fragments', value: '236' },
  ];
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 py-8">
      {metrics.map(m => (
        <div key={m.name} className="bg-gray-100 p-4 rounded shadow text-center">
          <div className="text-sm text-gray-500">{m.name}</div>
          <div className="text-xl font-semibold">{m.value}</div>
        </div>
      ))}
    </div>
  );
}
