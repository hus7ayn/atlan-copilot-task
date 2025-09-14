import React, { useState } from 'react';
import { Ticket } from '../types';
import TicketCard from './TicketCard';
import { Search, Filter, SortAsc, SortDesc } from 'lucide-react';

interface TicketDashboardProps {
  tickets: Ticket[];
}

type SortField = 'priority' | 'created_at' | 'confidence';
type SortDirection = 'asc' | 'desc';
type FilterType = 'all' | 'P0 (High)' | 'P1 (Medium)' | 'P2 (Low)';

const TicketDashboard: React.FC<TicketDashboardProps> = ({ tickets }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState<SortField>('priority');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
  const [filterPriority, setFilterPriority] = useState<FilterType>('all');
  const [filterSentiment, setFilterSentiment] = useState<string>('all');

  // Get unique sentiments for filter
  const uniqueSentiments = Array.from(
    new Set(tickets.map(t => t.classification.sentiment))
  );

  // Filter and sort tickets
  const filteredAndSortedTickets = tickets
    .filter(ticket => {
      const matchesSearch = 
        ticket.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
        ticket.body.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesPriority = filterPriority === 'all' || ticket.classification.priority === filterPriority;
      
      const matchesSentiment = filterSentiment === 'all' || 
        ticket.classification.sentiment === filterSentiment;
      
      return matchesSearch && matchesPriority && matchesSentiment;
    })
    .sort((a, b) => {
      let aValue: any, bValue: any;
      
      switch (sortField) {
        case 'priority':
          const priorityOrder = { 'P0 (High)': 0, 'P1 (Medium)': 1, 'P2 (Low)': 2 };
          aValue = priorityOrder[a.classification.priority as keyof typeof priorityOrder] ?? 3;
          bValue = priorityOrder[b.classification.priority as keyof typeof priorityOrder] ?? 3;
          break;
        case 'created_at':
          aValue = new Date(a.created_at).getTime();
          bValue = new Date(b.created_at).getTime();
          break;
        case 'confidence':
          aValue = a.classification.confidence;
          bValue = b.classification.confidence;
          break;
        default:
          return 0;
      }
      
      if (sortDirection === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  return (
    <div className="ticket-dashboard">
      <div className="dashboard-header">
        <h2>Classified Tickets ({filteredAndSortedTickets.length})</h2>
        
        <div className="dashboard-controls">
          <div className="search-container">
            <Search className="search-icon" />
            <input
              type="text"
              placeholder="Search tickets..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>
          
          <div className="filter-container">
            <Filter className="filter-icon" />
            <select
              value={filterPriority}
              onChange={(e) => setFilterPriority(e.target.value as FilterType)}
              className="filter-select"
            >
              <option value="all">All Priorities</option>
              <option value="P0 (High)">P0 (High)</option>
              <option value="P1 (Medium)">P1 (Medium)</option>
              <option value="P2 (Low)">P2 (Low)</option>
            </select>
            
            <select
              value={filterSentiment}
              onChange={(e) => setFilterSentiment(e.target.value)}
              className="filter-select"
            >
              <option value="all">All Sentiments</option>
              {uniqueSentiments.map(sentiment => (
                <option key={sentiment} value={sentiment}>{sentiment}</option>
              ))}
            </select>
          </div>
          
          <div className="sort-container">
            <button
              onClick={() => handleSort('priority')}
              className={`sort-button ${sortField === 'priority' ? 'active' : ''}`}
            >
              Priority {sortField === 'priority' && (sortDirection === 'asc' ? <SortAsc /> : <SortDesc />)}
            </button>
            <button
              onClick={() => handleSort('created_at')}
              className={`sort-button ${sortField === 'created_at' ? 'active' : ''}`}
            >
              Date {sortField === 'created_at' && (sortDirection === 'asc' ? <SortAsc /> : <SortDesc />)}
            </button>
            <button
              onClick={() => handleSort('confidence')}
              className={`sort-button ${sortField === 'confidence' ? 'active' : ''}`}
            >
              Confidence {sortField === 'confidence' && (sortDirection === 'asc' ? <SortAsc /> : <SortDesc />)}
            </button>
          </div>
        </div>
      </div>
      
      <div className="tickets-grid">
        {filteredAndSortedTickets.length === 0 ? (
          <div className="no-tickets">
            <p>No tickets found matching your criteria.</p>
          </div>
        ) : (
          filteredAndSortedTickets.map(ticket => (
            <TicketCard key={ticket.id} ticket={ticket} />
          ))
        )}
      </div>
    </div>
  );
};

export default TicketDashboard;
