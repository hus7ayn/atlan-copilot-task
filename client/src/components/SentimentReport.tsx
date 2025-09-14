import React, { useState, useEffect } from 'react';
import { SentimentReport as SentimentReportType } from '../types';

interface SentimentReportProps {
  onClose: () => void;
}

const SentimentReport: React.FC<SentimentReportProps> = ({ onClose }) => {
  const [report, setReport] = useState<SentimentReportType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSentimentReport();
  }, []);

  const fetchSentimentReport = async () => {
    try {
      setLoading(true);
      const [ticketsResponse, statsResponse] = await Promise.all([
        fetch('http://localhost:8000/api/tickets'),
        fetch('http://localhost:8000/api/stats')
      ]);
      
      if (!ticketsResponse.ok || !statsResponse.ok) {
        throw new Error('Failed to fetch sentiment report');
      }
      
      const ticketsData = await ticketsResponse.json();
      const statsData = await statsResponse.json();
      
      if (ticketsData.success && statsData.success) {
        // Convert the API response to the format expected by SentimentReport
        const convertedTickets = ticketsData.data.map((ticket: any) => ({
          id: ticket.id,
          subject: ticket.original_ticket?.subject || 'No subject',
          body: ticket.original_ticket?.body || 'No content',
          customer_email: ticket.original_ticket?.customer_email || 'unknown@example.com',
          created_at: ticket.original_ticket?.created_at || ticket.processed_at,
          classification: {
            topic_tags: ticket.classification.topicTags || [],
            sentiment: ticket.classification.sentiment?.[0]?.label || 'Neutral',
            priority: ticket.classification.priority || 'P2 (Low)',
            confidence: ticket.classification.sentiment?.[0]?.confidence || 0.5,
            reasoning: 'Auto-generated from API'
          }
        }));
        
        // Create the sentiment report structure
        const sentimentReport: SentimentReportType = {
          tickets: convertedTickets,
          summary: {
            total_tickets: statsData.data.totalTickets,
            sentiment_distribution: statsData.data.sentimentDistribution,
            topic_distribution: statsData.data.topicDistribution,
            priority_distribution: statsData.data.priorityDistribution,
            average_confidence: statsData.data.averageConfidence,
            high_confidence_tickets: convertedTickets.filter((t: any) => t.classification.confidence > 0.8).length,
            low_confidence_tickets: convertedTickets.filter((t: any) => t.classification.confidence < 0.6).length
          }
        };
        
        setReport(sentimentReport);
      } else {
        throw new Error('Failed to fetch data from server');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'Frustrated': return 'bg-red-100 text-red-800';
      case 'Angry': return 'bg-red-200 text-red-900';
      case 'Confused': return 'bg-yellow-100 text-yellow-800';
      case 'Curious': return 'bg-blue-100 text-blue-800';
      case 'Neutral': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    if (priority.includes('P0')) return 'bg-red-100 text-red-800';
    if (priority.includes('P1')) return 'bg-yellow-100 text-yellow-800';
    if (priority.includes('P2')) return 'bg-green-100 text-green-800';
    return 'bg-gray-100 text-gray-800';
  };

  const getTopicColor = (topic: string) => {
    const colors = {
      'How-to': 'bg-blue-100 text-blue-800',
      'Product': 'bg-purple-100 text-purple-800',
      'Connector': 'bg-green-100 text-green-800',
      'Lineage': 'bg-orange-100 text-orange-800',
      'API/SDK': 'bg-indigo-100 text-indigo-800',
      'SSO': 'bg-pink-100 text-pink-800',
      'Glossary': 'bg-teal-100 text-teal-800',
      'Best practices': 'bg-cyan-100 text-cyan-800',
      'Sensitive data': 'bg-red-100 text-red-800'
    };
    return colors[topic as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-3 text-lg">Loading sentiment report...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
          <div className="text-center">
            <div className="text-red-600 text-lg font-semibold mb-4">Error</div>
            <p className="text-gray-600 mb-4">{error}</p>
            <button
              onClick={onClose}
              className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!report) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-7xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-blue-600 text-white p-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold">Sentiment Analysis Report</h2>
            <button
              onClick={onClose}
              className="text-white hover:text-gray-200 text-xl"
            >
              ×
            </button>
          </div>
          <p className="mt-2 text-blue-100">
            Analysis of {report.summary.total_tickets} tickets from sample data
          </p>
        </div>

        {/* Summary Statistics */}
        <div className="p-6 border-b">
          <h3 className="text-lg font-semibold mb-4">Summary Statistics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{report.summary.total_tickets}</div>
              <div className="text-sm text-gray-600">Total Tickets</div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {report.summary.average_confidence}
              </div>
              <div className="text-sm text-gray-600">Avg Confidence</div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">
                {report.summary.high_confidence_tickets}
              </div>
              <div className="text-sm text-gray-600">High Confidence</div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">
                {report.summary.low_confidence_tickets}
              </div>
              <div className="text-sm text-gray-600">Low Confidence</div>
            </div>
          </div>
        </div>

        {/* Distribution Charts */}
        <div className="p-6 border-b">
          <div className="grid md:grid-cols-3 gap-6">
            {/* Sentiment Distribution */}
            <div>
              <h4 className="font-semibold mb-3">Sentiment Distribution</h4>
              <div className="space-y-2">
                {Object.entries(report.summary.sentiment_distribution).map(([sentiment, count]) => (
                  <div key={sentiment} className="flex justify-between items-center">
                    <span className="text-sm">{sentiment}</span>
                    <div className="flex items-center">
                      <div className="w-20 bg-gray-200 rounded-full h-2 mr-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{
                            width: `${(count / report.summary.total_tickets) * 100}%`
                          }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium">{count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Topic Distribution */}
            <div>
              <h4 className="font-semibold mb-3">Topic Distribution</h4>
              <div className="space-y-2">
                {Object.entries(report.summary.topic_distribution)
                  .sort(([,a], [,b]) => b - a)
                  .slice(0, 5)
                  .map(([topic, count]) => (
                  <div key={topic} className="flex justify-between items-center">
                    <span className="text-sm">{topic}</span>
                    <div className="flex items-center">
                      <div className="w-20 bg-gray-200 rounded-full h-2 mr-2">
                        <div
                          className="bg-green-600 h-2 rounded-full"
                          style={{
                            width: `${(count / report.summary.total_tickets) * 100}%`
                          }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium">{count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Priority Distribution */}
            <div>
              <h4 className="font-semibold mb-3">Priority Distribution</h4>
              <div className="space-y-2">
                {Object.entries(report.summary.priority_distribution).map(([priority, count]) => (
                  <div key={priority} className="flex justify-between items-center">
                    <span className="text-sm">{priority}</span>
                    <div className="flex items-center">
                      <div className="w-20 bg-gray-200 rounded-full h-2 mr-2">
                        <div
                          className="bg-red-600 h-2 rounded-full"
                          style={{
                            width: `${(count / report.summary.total_tickets) * 100}%`
                          }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium">{count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Tickets List */}
        <div className="p-6 max-h-96 overflow-y-auto">
          <h3 className="text-lg font-semibold mb-4">Individual Ticket Classifications</h3>
          <div className="space-y-4">
            {report.tickets.map((ticket) => (
              <div key={ticket.id} className="border rounded-lg p-4 hover:bg-gray-50">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-medium text-gray-900">{ticket.subject}</h4>
                  <span className="text-sm text-gray-500">{ticket.id}</span>
                </div>
                
                <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                  {ticket.body}
                </p>
                
                <div className="flex flex-wrap gap-2 mb-2">
                  {ticket.classification.topic_tags.map((topic: string) => (
                    <span
                      key={topic}
                      className={`px-2 py-1 rounded-full text-xs font-medium ${getTopicColor(topic)}`}
                    >
                      {topic}
                    </span>
                  ))}
                </div>
                
                <div className="flex items-center gap-4 text-sm">
                  <div className="flex items-center gap-1">
                    <span className="text-gray-500">Sentiment:</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSentimentColor(ticket.classification.sentiment)}`}>
                      {ticket.classification.sentiment}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-1">
                    <span className="text-gray-500">Priority:</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(ticket.classification.priority)}`}>
                      {ticket.classification.priority}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-1">
                    <span className="text-gray-500">Confidence:</span>
                    <span className="font-medium">
                      {(ticket.classification.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
                
                <div className="mt-2 text-xs text-gray-500">
                  <strong>Reasoning:</strong> {ticket.classification.reasoning}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SentimentReport;
