import { publications } from '../data/publications.js';

export default function Research() {
  return (
    <div className="p-4 space-y-4">
      <h2 className="text-xl font-semibold">Publications</h2>
      <ul className="list-disc list-inside space-y-1">
        {publications.map(p => (
          <li key={p.title}>
            <span className="font-medium">{p.title}</span> – {p.venue}
          </li>
        ))}
      </ul>
    </div>
  );
}
