export default function DiagramViewer({ analysis, onBack }) {
  return (
    <div>
      <button onClick={onBack} style={{ marginBottom: '1rem' }}>
        ← Back to repositories
      </button>
      
      <h2>Analysis: {analysis.repo}</h2>
      
      <div style={{ marginTop: '2rem' }}>
        <h3>Summary</h3>
        <ul>
          <li>Total files: {analysis.analysis.summary.total_files}</li>
          <li>Total functions: {analysis.analysis.summary.total_functions}</li>
          <li>Total classes: {analysis.analysis.summary.total_classes}</li>
        </ul>
      </div>

      <div style={{ marginTop: '2rem' }}>
        <h3>Files Analyzed</h3>
        {Object.entries(analysis.analysis.files).map(([filepath, data]) => (
          <details key={filepath} style={{ marginBottom: '1rem' }}>
            <summary style={{ cursor: 'pointer', fontWeight: 'bold' }}>
              {filepath}
            </summary>
            <pre style={{ 
              background: '#f5f5f5', 
              padding: '1rem', 
              overflow: 'auto',
              fontSize: '0.85rem'
            }}>
              {JSON.stringify(data, null, 2)}
            </pre>
          </details>
        ))}
      </div>

      <div style={{ marginTop: '2rem' }}>
        <h3>Dependency Graph</h3>
        <pre style={{ background: '#f5f5f5', padding: '1rem', overflow: 'auto' }}>
          {JSON.stringify(analysis.analysis.dependency_graph, null, 2)}
        </pre>
      </div>
    </div>
  );
}