import React, { useState } from 'react';
import { Ticket } from '../types';
import { 
  ChevronDown, 
  ChevronUp, 
  Tag, 
  AlertTriangle, 
  Clock, 
  User, 
  Calendar,
  MessageSquare
} from 'lucide-react';

interface TicketCardProps {
  ticket: Ticket;
}

const TicketCard: React.FC<TicketCardProps> = ({ ticket }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  // Use the ticket directly since it now has the fields we need
  
  const getPriorityColor = (priority: string) => {
    if (priority.includes('P0')) return '#ff4757';
    if (priority.includes('P1')) return '#ffa502';
    return '#2ed573';
  };

  const getSentimentColor = (sentiment: string) => {
    const colors: Record<string, string> = {
      'Angry': '#ff4757',
      'Frustrated': '#ff6b6b',
      'Curious': '#4ecdc4',
      'Confused': '#ffa502',
      'Neutral': '#95a5a6'
    };
    return colors[sentiment] || '#95a5a6';
  };

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'Angry': return '😠';
      case 'Frustrated': return '😤';
      case 'Curious': return '🤔';
      case 'Confused': return '😕';
      case 'Neutral': return '😐';
      default: return '😐';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // const truncateText = (text: string, maxLength: number) => {
  //   if (text.length <= maxLength) return text;
  //   return text.substring(0, maxLength) + '...';
  // };

  return (
    <div className="ticket-card">
      <div className="ticket-header" onClick={() => setIsExpanded(!isExpanded)}>
        <div className="ticket-title-section">
          <h3 className="ticket-title">{ticket.subject}</h3>
          <div className="ticket-meta">
            <span className="ticket-id">#{ticket.id}</span>
            <span className="ticket-date">
              <Calendar className="meta-icon" />
              {formatDate(ticket.created_at)}
            </span>
          </div>
        </div>
        
          <div className="ticket-classifications">
          {/* Priority Badge */}
          <div 
            className="priority-badge"
            style={{ backgroundColor: getPriorityColor(ticket.classification.priority) }}
          >
            <AlertTriangle className="priority-icon" />
            {ticket.classification.priority}
          </div>
          
          {/* Sentiment Badge */}
          <div className="sentiment-badges">
            <div
              className="sentiment-badge"
              style={{ backgroundColor: getSentimentColor(ticket.classification.sentiment) }}
              title={`Sentiment: ${ticket.classification.sentiment} (${(ticket.classification.confidence * 100).toFixed(1)}% confidence)`}
            >
              <span className="sentiment-emoji">{getSentimentIcon(ticket.classification.sentiment)}</span>
              <span className="sentiment-label">{ticket.classification.sentiment}</span>
              <span className="sentiment-confidence">{(ticket.classification.confidence * 100).toFixed(0)}%</span>
            </div>
          </div>
        </div>
        
        <div className="expand-button">
          {isExpanded ? <ChevronUp /> : <ChevronDown />}
        </div>
      </div>
      
      {/* Topic Tags Section */}
      <div className="ticket-tags">
        <span className="tags-label">Topic Tags:</span>
        {ticket.classification.topic_tags.map((tag, index) => (
          <span key={index} className="topic-tag">
            <Tag className="tag-icon" />
            {tag}
          </span>
        ))}
      </div>
      
      {isExpanded && (
        <div className="ticket-details">
          <div className="ticket-body">
            <h4>
              <MessageSquare className="section-icon" />
              Ticket Content
            </h4>
            <p className="ticket-body-text">{ticket.body}</p>
          </div>
          
          <div className="ticket-customer">
            <h4>
              <User className="section-icon" />
              Customer Information
            </h4>
            <p className="customer-email">{ticket.customer_email}</p>
          </div>
          
          <div className="ticket-processing">
            <h4>
              <Clock className="section-icon" />
              Processing Information
            </h4>
            <p className="processed-at">
              Created: {formatDate(ticket.created_at)}
            </p>
          </div>
          
          <div className="classification-details">
            <h4>Detailed Classification</h4>
            <div className="classification-grid">
              <div className="classification-section">
                <h5>Topic Tags</h5>
                <div className="tags-list">
                  {ticket.classification.topic_tags.map((tag, index) => (
                    <span key={index} className="detail-tag">{tag}</span>
                  ))}
                </div>
              </div>
              
              <div className="classification-section">
                <h5>Sentiment Analysis</h5>
                <div className="sentiment-details">
                  <div className="sentiment-detail">
                    <span className="sentiment-name">{ticket.classification.sentiment}</span>
                    <div className="confidence-bar">
                      <div 
                        className="confidence-fill"
                        style={{ 
                          width: `${ticket.classification.confidence * 100}%`,
                          backgroundColor: getSentimentColor(ticket.classification.sentiment)
                        }}
                      ></div>
                    </div>
                    <span className="confidence-value">{(ticket.classification.confidence * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </div>
              
              <div className="classification-section">
                <h5>Priority Assessment</h5>
                <div className="priority-detail">
                  <span 
                    className="priority-value"
                    style={{ color: getPriorityColor(ticket.classification.priority) }}
                  >
                    {ticket.classification.priority}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TicketCard;
