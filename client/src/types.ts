export interface SentimentResult {
  label: string;
  confidence: number;
}

export interface Classification {
  topicTags: string[];
  sentiment: SentimentResult[];
  priority: string;
}

export interface OriginalTicket {
  subject: string;
  body: string;
  created_at: string;
  customer_email: string;
}

export interface ProcessedTicket {
  id: string;
  originalTicket?: OriginalTicket;
  original_ticket?: OriginalTicket;
  classification: Classification;
  processed_at: string;
  error?: string;
}

export interface ClassificationStats {
  totalTickets: number;
  topicDistribution: Record<string, number>;
  sentimentDistribution: Record<string, number>;
  priorityDistribution: Record<string, number>;
  averageConfidence: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface TicketsResponse {
  success: boolean;
  data: Ticket[];
  stats?: ClassificationStats;
  count: number;
}

export interface ClassificationResult {
  topic: string[];
  sentiment: SentimentResult[];
  priority: string;
  reasoning: string;
}

export interface RAGResponse {
  answer: string;
  sources: string[];
  topic: string;
}

// New types for the enhanced system
export interface TicketClassification {
  topic_tags: string[];
  sentiment: string;
  priority: string;
  confidence: number;
  reasoning: string;
}

export interface Ticket {
  id: string;
  subject: string;
  body: string;
  customer_email: string;
  created_at: string;
  classification: TicketClassification;
}

export interface SentimentReport {
  tickets: Ticket[];
  summary: {
    total_tickets: number;
    sentiment_distribution: Record<string, number>;
    topic_distribution: Record<string, number>;
    priority_distribution: Record<string, number>;
    average_confidence: number;
    high_confidence_tickets: number;
    low_confidence_tickets: number;
  };
}

export interface TicketResponse {
  analysis: {
    topic_tags: string[];
    sentiment: string;
    priority: string;
    confidence: number;
    reasoning: string;
    evidence: {
      topic_confidence: number;
      sentiment_confidence: number;
      priority_score: number;
    };
  };
  final_response: string;
  sources: string[] | null;
}
