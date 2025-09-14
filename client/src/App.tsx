import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import TicketDashboard from './components/TicketDashboard';
import Header from './components/Header';
import StatsOverview from './components/StatsOverview';
import FileUpload from './components/FileUpload';
import SentimentReport from './components/SentimentReport';
import InteractiveAgentPage from './pages/InteractiveAgentPage';
import './pages/InteractiveAgentPage.css';
import { Ticket, ClassificationStats } from './types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [stats, setStats] = useState<ClassificationStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showSentimentReport, setShowSentimentReport] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'error'>('connecting');

  useEffect(() => {
    fetchTickets();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchTickets = async (retryCount = 0) => {
    try {
      setLoading(true);
      console.log('Fetching from:', API_BASE_URL, 'Retry:', retryCount);
      
      // First check if backend is healthy
      const healthResponse = await fetch(`${API_BASE_URL}/api/health`);
      if (!healthResponse.ok) {
        throw new Error(`Backend not healthy: ${healthResponse.status}`);
      }
      console.log('Backend health check passed');
      
      const [ticketsResponse, statsResponse] = await Promise.all([
        fetch(`${API_BASE_URL}/api/tickets`),
        fetch(`${API_BASE_URL}/api/stats`)
      ]);
      
      console.log('Tickets response status:', ticketsResponse.status);
      console.log('Stats response status:', statsResponse.status);
      
      if (!ticketsResponse.ok) {
        throw new Error(`Tickets API error: ${ticketsResponse.status}`);
      }
      if (!statsResponse.ok) {
        throw new Error(`Stats API error: ${statsResponse.status}`);
      }
      
      const ticketsData = await ticketsResponse.json();
      const statsData = await statsResponse.json();
      
      if (ticketsData.tickets && statsData.total_tickets !== undefined) {
        // Use the classification data from the API response
        const convertedTickets = ticketsData.tickets.map((ticket: any) => ({
          id: ticket.id,
          subject: ticket.subject || 'No subject',
          body: ticket.body || 'No content',
          customer_email: ticket.customer_email || 'unknown@example.com',
          created_at: ticket.created_at || new Date().toISOString(),
          classification: {
            topic_tags: ticket.classification?.topic_tags || [],
            sentiment: ticket.classification?.sentiment || 'Neutral',
            priority: ticket.classification?.priority || 'P2 (Low)',
            confidence: ticket.classification?.confidence || 0.5,
            reasoning: ticket.classification?.reasoning || 'Classification data not available'
          }
        }));
        
        setTickets(convertedTickets);
        
        // Calculate stats from the actual ticket data
        const sentimentCounts: Record<string, number> = {};
        const topicCounts: Record<string, number> = {};
        const priorityCounts: Record<string, number> = {};
        let totalConfidence = 0;
        
        convertedTickets.forEach((ticket: Ticket) => {
          // Count sentiments
          const sentiment = ticket.classification.sentiment;
          sentimentCounts[sentiment] = (sentimentCounts[sentiment] || 0) + 1;
          
          // Count topics
          ticket.classification.topic_tags.forEach(tag => {
            topicCounts[tag] = (topicCounts[tag] || 0) + 1;
          });
          
          // Count priorities
          const priority = ticket.classification.priority;
          priorityCounts[priority] = (priorityCounts[priority] || 0) + 1;
          
          // Sum confidence
          totalConfidence += ticket.classification.confidence;
        });
        
        setStats({
          totalTickets: convertedTickets.length,
          sentimentDistribution: sentimentCounts,
          topicDistribution: topicCounts,
          priorityDistribution: priorityCounts,
          averageConfidence: convertedTickets.length > 0 ? totalConfidence / convertedTickets.length : 0
        });
        setError(null);
        setConnectionStatus('connected');
      } else {
        setError('Failed to fetch tickets or stats');
        setConnectionStatus('error');
      }
    } catch (err) {
      console.error('Error fetching tickets:', err);
      
      // Retry logic - retry up to 3 times with exponential backoff
      if (retryCount < 3) {
        console.log(`Retrying in ${Math.pow(2, retryCount)} seconds...`);
        setTimeout(() => {
          fetchTickets(retryCount + 1);
        }, Math.pow(2, retryCount) * 1000);
        return;
      }
      
      setError('Error connecting to server');
      setConnectionStatus('error');
    } finally {
      setLoading(false);
    }
  };

  const reclassifyTickets = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/reclassify`, {
        method: 'POST',
      });
      const data = await response.json();
      
      if (data.success) {
        setTickets(data.data);
        // Fetch updated stats
        const statsResponse = await fetch(`${API_BASE_URL}/api/stats`);
        const statsData = await statsResponse.json();
        if (statsData.success) {
          setStats(statsData.stats);
        }
        setError(null);
      } else {
        setError('Failed to reclassify tickets');
      }
    } catch (err) {
      setError('Error reclassifying tickets');
      console.error('Error reclassifying tickets:', err);
    } finally {
      setLoading(false);
    }
  };


  if (loading) {
    return (
      <div className="app">
        <Header onReclassify={reclassifyTickets} loading={loading} connectionStatus={connectionStatus} />
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading AI-powered ticket classifications...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app">
        <Header onReclassify={reclassifyTickets} loading={loading} connectionStatus={connectionStatus} />
        <div className="error-container">
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={() => fetchTickets()} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <Routes>
        {/* Main Dashboard Route */}
        <Route path="/" element={
          <div className="app">
            <Header onReclassify={reclassifyTickets} loading={loading} connectionStatus={connectionStatus} />
            <main className="main-content">
              {/* New Action Buttons */}
              <div className="action-buttons mb-6">
                <button
                  onClick={() => setShowSentimentReport(true)}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 mr-4"
                >
                  📊 View Sentiment Report
                </button>
                <Link
                  to="/interactive-agent"
                  className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 inline-block"
                >
                  🤖 Interactive AI Agent
                </Link>
              </div>
              
              <FileUpload onUploadSuccess={fetchTickets} />
              <StatsOverview stats={stats} />
              <TicketDashboard tickets={tickets} />
            </main>
            
            {/* Modals */}
            {showSentimentReport && (
              <SentimentReport onClose={() => setShowSentimentReport(false)} />
            )}
          </div>
        } />
        
        {/* Interactive Agent Route */}
        <Route path="/interactive-agent" element={<InteractiveAgentPage />} />
      </Routes>
    </Router>
  );
}

export default App;