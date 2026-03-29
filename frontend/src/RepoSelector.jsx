import React, { useState, useEffect } from 'react';  

const API_URL = 'http://localhost:8000';

export default function RepoSelector({ accessToken, onRepoSelected, loading }) {
  const [repos, setRepos] = useState([]);
  const [fetchingRepos, setFetchingRepos] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/repos?access_token=${accessToken}`)
      .then(res => res.json())
      .then(data => {
        setRepos(data.repositories);
        setFetchingRepos(false);
      });
  }, [accessToken]);

  if (fetchingRepos) {
    return <div>Loading your repositories...</div>;
  }

  return (
    <div>
      <h2>Select a Repository</h2>
      <p>Choose a Python repository to analyze:</p>
      
      {loading && <div style={{ padding: '2rem', textAlign: 'center' }}>
        <div>Analyzing repository... This may take a minute.</div>
      </div>}
      
      <div style={{ display: 'grid', gap: '1rem', marginTop: '2rem' }}>
        {repos
          .filter(repo => repo.language === 'Python')
          .map(repo => (
            <div 
              key={repo.full_name}
              style={{
                border: '1px solid #ddd',
                padding: '1rem',
                borderRadius: '6px',
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.5 : 1
              }}
              onClick={() => !loading && onRepoSelected(repo)}
            >
              <h3>{repo.name}</h3>
              <p style={{ color: '#666', fontSize: '0.9rem' }}>
                {repo.description || 'No description'}
              </p>
              <small>{repo.language}</small>
            </div>
          ))}
      </div>
    </div>
  );
}