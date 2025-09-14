import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Send, Brain, Zap, AlertCircle, CheckCircle, Clock, Target, MessageSquare, ArrowLeft, Home } from 'lucide-react';

interface InternalAnalysis {
  topic_tags: string[];
  sentiment: string;
  priority: string;
  confidence: number;
  reasoning: string;
  classification_time: string;
}

interface FinalResponse {
  answer: string;
  sources: Array<{
    title: string;
    url: string;
    snippet: string;
  }>;
  confidence: number;
  is_tavily_used: boolean;
  routing_message?: string;
}

interface AgentResponse {
  internal_analysis: InternalAnalysis;
  final_response: FinalResponse;
  processing_method: 'tavily' | 'routed';
}

const InteractiveAgentPage: React.FC = () => {
  const navigate = useNavigate();
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<AgentResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    console.log('Form submitted with text:', inputText);
    
    if (!inputText.trim()) {
      console.log('Empty input, returning');
      return;
    }

    console.log('Starting processing...');
    setIsLoading(true);
    setError(null);
    setResponse(null);
    setLoadingStep('🔍 Analyzing your query...');

    try {
      console.log('Making request to Simple Tavily System...');
      
      // Step 1: Classification
      setLoadingStep('🧠 Classifying topic and sentiment...');
      await new Promise(resolve => setTimeout(resolve, 500)); // Reduced simulation time
      
      const res = await fetch('http://localhost:8000/api/interactive-agent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: inputText,
          channel: 'interactive'
        }),
      });

      console.log('Response status:', res.status);

      if (!res.ok) {
        const errorText = await res.text();
        console.error('Error response:', errorText);
        throw new Error(`HTTP error! status: ${res.status} - ${errorText}`);
      }

      const data = await res.json();
      console.log('Response data:', data);
      
      // Step 2: Processing based on classification
      if (data.internal_analysis.topic_tags.some((tag: string) => 
        ['Product', 'Best practices', 'API/SDK', 'SSO', 'Connector'].includes(tag)
      )) {
        setLoadingStep('🔍 Searching Atlan documentation with Tavily...');
        await new Promise(resolve => setTimeout(resolve, 800)); // Reduced simulation time
      } else {
        setLoadingStep('📋 Routing to appropriate team...');
        await new Promise(resolve => setTimeout(resolve, 400)); // Reduced simulation time
      }
      
      setResponse(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
      setLoadingStep('');
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'P1 (High)': return 'text-red-600 bg-red-100';
      case 'P2 (Medium)': return 'text-yellow-600 bg-yellow-100';
      case 'P3 (Low)': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case 'positive': return 'text-green-600 bg-green-100';
      case 'negative': return 'text-red-600 bg-red-100';
      case 'neutral': return 'text-blue-600 bg-blue-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="interactive-agent-page">
      {/* Header */}
      <div className="page-header">
        <div className="header-content">
          <div className="header-left">
            <button
              onClick={() => navigate('/')}
              className="back-button"
              title="Back to Dashboard"
            >
              <ArrowLeft className="back-icon" />
            </button>
            <div className="header-info">
              <Brain className="header-icon" />
              <div>
                <h1>Atlan Customer Copilot</h1>
                <p>Interactive AI Agent with Real-time Documentation Search</p>
              </div>
            </div>
          </div>
          <button
            onClick={() => navigate('/')}
            className="home-button"
            title="Go to Dashboard"
          >
            <Home className="home-icon" />
            Dashboard
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="page-content">
        {/* Input Section */}
        <div className="input-section">
          <form onSubmit={handleSubmit} className="input-form">
            <div className="input-group">
              <MessageSquare className="input-icon" />
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !isLoading && inputText.trim()) {
                    handleSubmit(e as any);
                  }
                }}
                placeholder="Ask a question about Atlan..."
                className="input-field"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !inputText.trim()}
                className="submit-button"
              >
                {isLoading ? (
                  <Clock className="button-icon animate-spin" />
                ) : (
                  <Send className="button-icon" />
                )}
                {isLoading ? 'Processing...' : 'Ask'}
              </button>
            </div>
          </form>
        </div>

        {/* Loading Display */}
        {isLoading && (
          <div className="loading-container">
            <div className="loading-content">
              <div className="loading-spinner">
                <Clock className="spinner-icon animate-spin" />
              </div>
              <div className="loading-text">
                <h3>Processing Your Query</h3>
                <p className="loading-step">{loadingStep}</p>
                <div className="loading-steps">
                  <div className="step-item">
                    <Brain className="step-icon" />
                    <span>1. Classifying topic and sentiment</span>
                  </div>
                  <div className="step-item">
                    <Target className="step-icon" />
                    <span>2. Determining processing method</span>
                  </div>
                  <div className="step-item">
                    <Zap className="step-icon" />
                    <span>3. Generating response</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="error-container">
            <AlertCircle className="error-icon" />
            <p className="error-message">{error}</p>
          </div>
        )}

        {/* Dual Panel Results */}
        {response && (
          <div className="dual-panel-results">
            {/* Left Panel - Internal Analysis */}
            <div className="panel left-panel">
              <div className="panel-header">
                <Target className="panel-icon" />
                <h3>Internal Analysis</h3>
                <span className="panel-subtitle">AI Classification Details</span>
              </div>
              
              <div className="panel-content">
                {/* Topic Tags */}
                <div className="analysis-section">
                  <h4>Topic Classification</h4>
                  <div className="tags-container">
                    {response.internal_analysis.topic_tags.map((tag, index) => (
                      <span key={index} className="topic-tag">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Sentiment & Priority */}
                <div className="analysis-row">
                  <div className="analysis-item">
                    <h4>Sentiment</h4>
                    <span className={`status-badge ${getSentimentColor(response.internal_analysis.sentiment)}`}>
                      {response.internal_analysis.sentiment}
                    </span>
                  </div>
                  <div className="analysis-item">
                    <h4>Priority</h4>
                    <span className={`status-badge ${getPriorityColor(response.internal_analysis.priority)}`}>
                      {response.internal_analysis.priority}
                    </span>
                  </div>
                </div>

                {/* Confidence */}
                <div className="analysis-section">
                  <h4>Confidence Score</h4>
                  <div className="confidence-bar">
                    <div 
                      className="confidence-fill" 
                      style={{ width: `${response.internal_analysis.confidence * 100}%` }}
                    />
                    <span className="confidence-text">
                      {Math.round(response.internal_analysis.confidence * 100)}%
                    </span>
                  </div>
                </div>

                {/* Reasoning */}
                <div className="analysis-section">
                  <h4>AI Reasoning</h4>
                  <p className="reasoning-text">
                    {response.internal_analysis.reasoning}
                  </p>
                </div>

                {/* Processing Method */}
                <div className="analysis-section">
                  <h4>Processing Method</h4>
                  <div className="method-indicator">
                    {response.processing_method === 'tavily' ? (
                      <>
                        <Zap className="method-icon text-green-600" />
                        <span className="method-text">Tavily Real-time Search</span>
                      </>
                    ) : (
                      <>
                        <AlertCircle className="method-icon text-orange-600" />
                        <span className="method-text">Routed to Team</span>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Right Panel - Final Response */}
            <div className="panel right-panel">
              <div className="panel-header">
                <CheckCircle className="panel-icon" />
                <h3>Final Response</h3>
                <span className="panel-subtitle">
                  {response.final_response.is_tavily_used ? 'Tavily Documentation Answer' : 'Team Routing Message'}
                </span>
              </div>
              
              <div className="panel-content">
                {/* Answer */}
                <div className="response-section">
                  <h4>Answer</h4>
                  <div className="answer-content">
                    {response.final_response.is_tavily_used ? (
                      <div className="tavily-answer">
                        <div className="answer-text">
                          {response.final_response.answer}
                        </div>
                        {response.final_response.confidence > 0 && (
                          <div className="answer-confidence">
                            <span className="confidence-label">Confidence:</span>
                            <span className="confidence-value">
                              {Math.round(response.final_response.confidence * 100)}%
                            </span>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="routing-message">
                        <AlertCircle className="routing-icon" />
                        <div className="routing-text">
                          {response.final_response.routing_message}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Sources (only for Tavily responses) */}
                {response.final_response.is_tavily_used && response.final_response.sources.length > 0 && (
                  <div className="response-section">
                    <h4>Sources</h4>
                    <div className="sources-list">
                      {response.final_response.sources.map((source, index) => (
                        <div key={index} className="source-item">
                          <a 
                            href={source.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="source-link"
                          >
                            {source.title}
                          </a>
                          <p className="source-snippet">{source.snippet}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Processing Info */}
                <div className="response-section">
                  <h4>Processing Information</h4>
                  <div className="processing-info">
                    <div className="info-item">
                      <span className="info-label">Method:</span>
                      <span className="info-value">
                        {response.processing_method === 'tavily' ? 'Tavily Search' : 'Team Routing'}
                      </span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Timestamp:</span>
                      <span className="info-value">
                        {new Date(response.internal_analysis.classification_time).toLocaleString()}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default InteractiveAgentPage;
