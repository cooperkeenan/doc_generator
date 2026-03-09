import { useState, useEffect } from 'react';
import GitHubAuth from './GitHubAuth';
import RepoSelector from './RepoSelector';
import DiagramViewer from './DiagramViewer';

const API_URL = 'http://localhost:8000';

function App() {
  const [accessToken, setAccessToken] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  // Handle OAuth callback
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');
    
    if (code && !accessToken) {
      // Exchange code for token
      fetch(`${API_URL}/auth/github/callback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
      })
        .then(res => res.json())
        .then(data => {
          setAccessToken(data.access_token);
          // Clean URL
          window.history.replaceState({}, '', '/');
        });
    }
  }, []);

  const handleRepoSelected = async (repo) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          repo_owner: repo.owner,
          repo_name: repo.name,
          access_token: accessToken
        })
      });
      const data = await response.json();
      setAnalysis(data);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>📊 Code Documentation Generator</h1>
      
      {!accessToken ? (
        <GitHubAuth />
      ) : !analysis ? (
        <RepoSelector 
          accessToken={accessToken} 
          onRepoSelected={handleRepoSelected}
          loading={loading}
        />
      ) : (
        <DiagramViewer analysis={analysis} onBack={() => setAnalysis(null)} />
      )}
    </div>
  );
}

export default App;