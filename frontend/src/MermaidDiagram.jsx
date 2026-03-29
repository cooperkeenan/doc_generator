import React, { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({ 
  startOnLoad: false,
  theme: 'default',
  securityLevel: 'loose',
});

export default function MermaidDiagram({ chart, title }) {
  const ref = useRef(null);

  useEffect(() => {
    if (ref.current && chart) {
      try {
        mermaid.render(`mermaid-${Date.now()}`, chart).then(({ svg }) => {
          ref.current.innerHTML = svg;
        });
      } catch (error) {
        console.error('Mermaid rendering error:', error);
        ref.current.innerHTML = `<pre>Error rendering diagram: ${error.message}</pre>`;
      }
    }
  }, [chart]);

  return (
    <div style={{ marginTop: '2rem' }}>
      <h3>{title}</h3>
      <div 
        ref={ref} 
        style={{ 
          border: '1px solid #ddd', 
          padding: '1rem',
          background: 'white',
          borderRadius: '6px',
          overflow: 'auto'
        }}
      />
      <details style={{ marginTop: '1rem' }}>
        <summary style={{ cursor: 'pointer', color: '#666' }}>
          View Mermaid Code
        </summary>
        <pre style={{ 
          background: '#f5f5f5', 
          padding: '1rem',
          fontSize: '0.85rem',
          overflow: 'auto'
        }}>
          {chart}
        </pre>
      </details>
    </div>
  );
}