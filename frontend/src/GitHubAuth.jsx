import React from 'react';  

const GITHUB_CLIENT_ID = 'Ov23liff91VGCpUNWcXc';
const REDIRECT_URI = 'http://localhost:5173';

export default function GitHubAuth() {
  const handleLogin = () => {
    const authUrl = `https://github.com/login/oauth/authorize?client_id=${GITHUB_CLIENT_ID}&redirect_uri=${REDIRECT_URI}&scope=repo`;
    window.location.href = authUrl;
  };

  return (
    <div style={{ textAlign: 'center', marginTop: '4rem' }}>
      <h2>Connect your GitHub account</h2>
      <p>We'll analyze your repositories to generate documentation</p>
      <button 
        onClick={handleLogin}
        style={{
          padding: '1rem 2rem',
          fontSize: '1.1rem',
          cursor: 'pointer',
          backgroundColor: '#24292e',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          marginTop: '2rem'
        }}
      >
        Connect with GitHub
      </button>
    </div>
  );
}