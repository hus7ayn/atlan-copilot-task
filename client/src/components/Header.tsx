import React from 'react';
import { RefreshCw, Brain } from 'lucide-react';

interface HeaderProps {
  onReclassify: () => void;
  loading: boolean;
  connectionStatus?: 'connecting' | 'connected' | 'error';
}

const Header: React.FC<HeaderProps> = ({ onReclassify, loading, connectionStatus = 'connecting' }) => {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <div className="logo">
            <Brain className="logo-icon" />
            <h1>Atlan Customer Copilot</h1>
          </div>
          <p className="subtitle">AI-Powered Support Ticket Classification</p>
        </div>
        
        <div className="header-right">
          <div className="connection-status">
            <div className={`status-indicator ${connectionStatus}`}>
              {connectionStatus === 'connected' && '🟢 Connected'}
              {connectionStatus === 'connecting' && '🟡 Connecting...'}
              {connectionStatus === 'error' && '🔴 Connection Error'}
            </div>
          </div>
          <button 
            onClick={onReclassify} 
            disabled={loading}
            className="reclassify-button"
            title="Reclassify all tickets"
          >
            <RefreshCw className={`refresh-icon ${loading ? 'spinning' : ''}`} />
            {loading ? 'Reclassifying...' : 'Reclassify'}
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
