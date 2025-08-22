import React from 'react';
import { Shield, TrendingUp, TrendingDown, Minus } from 'lucide-react';

const CreditScoreDisplay = ({ company, creditScore }) => {
  const getScoreColor = (score) => {
    if (score >= 80) return '#10b981'; // green
    if (score >= 60) return '#f59e0b'; // yellow
    if (score >= 40) return '#f97316'; // orange
    return '#ef4444'; // red
  };

  const getScoreGrade = (score) => {
    if (score >= 90) return 'AAA';
    if (score >= 80) return 'AA';
    if (score >= 70) return 'A';
    if (score >= 60) return 'BBB';
    if (score >= 50) return 'BB';
    if (score >= 40) return 'B';
    return 'CCC';
  };

  const getRiskLevel = (score) => {
    if (score >= 80) return { level: 'Low Risk', icon: TrendingUp };
    if (score >= 60) return { level: 'Medium Risk', icon: Minus };
    return { level: 'High Risk', icon: TrendingDown };
  };

  const risk = getRiskLevel(creditScore);
  const RiskIcon = risk.icon;

  return (
    <div className="card">
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
        <Shield size={20} />
        <h3>Credit Score Analysis</h3>
      </div>

      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <h2 style={{ 
          fontSize: '1.5rem', 
          fontWeight: 'bold', 
          color: '#1f2937',
          marginBottom: '0.5rem' 
        }}>
          {company.name} ({company.ticker})
        </h2>
        <div style={{ 
          fontSize: '3rem', 
          fontWeight: 'bold', 
          color: getScoreColor(creditScore),
          lineHeight: '1'
        }}>
          {creditScore}
        </div>
        <div style={{ 
          fontSize: '1.25rem', 
          fontWeight: '600', 
          color: getScoreColor(creditScore),
          marginTop: '0.5rem'
        }}>
          {getScoreGrade(creditScore)}
        </div>
      </div>

      {/* Score Bar */}
      <div style={{ marginBottom: '1.5rem' }}>
        <div style={{
          width: '100%',
          height: '12px',
          backgroundColor: '#e5e7eb',
          borderRadius: '6px',
          overflow: 'hidden'
        }}>
          <div style={{
            width: `${creditScore}%`,
            height: '100%',
            backgroundColor: getScoreColor(creditScore),
            borderRadius: '6px',
            transition: 'width 1s ease-in-out'
          }} />
        </div>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: '0.75rem',
          color: '#6b7280',
          marginTop: '0.25rem'
        }}>
          <span>0</span>
          <span>25</span>
          <span>50</span>
          <span>75</span>
          <span>100</span>
        </div>
      </div>

      {/* Risk Assessment */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '0.5rem',
        padding: '1rem',
        backgroundColor: '#f8fafc',
        borderRadius: '8px'
      }}>
        <RiskIcon size={20} color={getScoreColor(creditScore)} />
        <span style={{ 
          fontWeight: '600', 
          color: getScoreColor(creditScore)
        }}>
          {risk.level}
        </span>
      </div>

      {/* Key Metrics */}
      <div style={{
        marginTop: '1.5rem',
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '1rem'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>Debt Ratio</div>
          <div style={{ fontWeight: '600', color: '#1f2937' }}>
            {(company.debtRatio * 100).toFixed(1)}%
          </div>
        </div>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>ROE</div>
          <div style={{ fontWeight: '600', color: '#1f2937' }}>
            {(company.roe * 100).toFixed(1)}%
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreditScoreDisplay;