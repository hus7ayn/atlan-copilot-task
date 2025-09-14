import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { ClassificationStats } from '../types';
import { TrendingUp, Users } from 'lucide-react';

interface StatsOverviewProps {
  stats: ClassificationStats | null;
}

const COLORS = {
  topics: ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1', '#d084d0', '#87d068', '#ffc658', '#ff7300'],
  sentiments: ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', '#ff9ff3'],
  priorities: ['#ff4757', '#ffa502', '#2ed573']
};

interface ChartDataItem {
  name: string;
  value: number;
  percentage: string;
}

const StatsOverview: React.FC<StatsOverviewProps> = ({ stats }) => {
  if (!stats) {
    return (
      <div className="stats-overview">
        <h2>Loading statistics...</h2>
      </div>
    );
  }

  const topicData: ChartDataItem[] = Object.entries(stats.topicDistribution || {}).map(([name, value]) => ({
    name,
    value,
    percentage: stats.totalTickets > 0 ? ((value / stats.totalTickets) * 100).toFixed(1) : '0.0'
  }));

  const sentimentData: ChartDataItem[] = Object.entries(stats.sentimentDistribution || {}).map(([name, value]) => ({
    name,
    value,
    percentage: stats.totalTickets > 0 ? ((value / stats.totalTickets) * 100).toFixed(1) : '0.0'
  }));

  const priorityData: ChartDataItem[] = Object.entries(stats.priorityDistribution || {}).map(([name, value]) => ({
    name,
    value,
    percentage: stats.totalTickets > 0 ? ((value / stats.totalTickets) * 100).toFixed(1) : '0.0'
  }));

  const getPriorityColor = (priority: string) => {
    if (priority.includes('P0')) return '#ff4757';
    if (priority.includes('P1')) return '#ffa502';
    return '#2ed573';
  };

  return (
    <div className="stats-overview">
      <div className="stats-header">
        <h2>Classification Overview</h2>
        <div className="stats-summary">
          <div className="stat-item">
            <Users className="stat-icon" />
            <span className="stat-value">{stats.totalTickets}</span>
            <span className="stat-label">Total Tickets</span>
          </div>
          <div className="stat-item">
            <TrendingUp className="stat-icon" />
            <span className="stat-value">{(stats.averageConfidence * 100).toFixed(1)}%</span>
            <span className="stat-label">Avg Confidence</span>
          </div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-container">
          <h3>Topic Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topicData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="name" 
                angle={-45}
                textAnchor="end"
                height={80}
                fontSize={12}
              />
              <YAxis />
              <Tooltip 
                formatter={(value: any, name: string) => [
                  `${value} tickets (${topicData.find(d => d.name === name)?.percentage}%)`,
                  'Count'
                ]}
              />
              <Bar dataKey="value" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Sentiment Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={sentimentData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(props: any) => {
                  const { name, value } = props;
                  const percentage = value && stats.totalTickets > 0 
                    ? ((value / stats.totalTickets) * 100).toFixed(1) 
                    : '0.0';
                  return `${name || 'Unknown'}: ${percentage}%`;
                }}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {sentimentData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS.sentiments[index % COLORS.sentiments.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value: any) => [`${value} tickets`, 'Count']} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Priority Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={priorityData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip 
                formatter={(value: any, name: string) => [
                  `${value} tickets (${priorityData.find(d => d.name === name)?.percentage}%)`,
                  'Count'
                ]}
              />
              <Bar dataKey="value" fill="#8884d8">
                {priorityData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getPriorityColor(entry.name)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default StatsOverview;
