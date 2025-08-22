import React from 'react';
import { Search, Building2 } from 'lucide-react';

const CompanySelector = ({ companies, selectedCompany, onCompanySelect }) => {
  return (
    <div className="card">
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
        <Search size={20} />
        <h2 style={{ color: '#1f2937', fontSize: '1.25rem', fontWeight: '600' }}>
          Select Company
        </h2>
      </div>
      
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '1rem'
      }}>
        {companies.map((company) => (
          <button
            key={company.ticker}
            onClick={() => onCompanySelect(company.ticker)}
            style={{
              padding: '1rem',
              border: selectedCompany?.ticker === company.ticker ? '2px solid #3b82f6' : '2px solid #e5e7eb',
              borderRadius: '8px',
              background: selectedCompany?.ticker === company.ticker ? '#eff6ff' : 'white',
              cursor: 'pointer',
              transition: 'all 0.2s',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              textAlign: 'left'
            }}
            onMouseEnter={(e) => {
              if (selectedCompany?.ticker !== company.ticker) {
                e.target.style.borderColor = '#9ca3af';
                e.target.style.background = '#f9fafb';
              }
            }}
            onMouseLeave={(e) => {
              if (selectedCompany?.ticker !== company.ticker) {
                e.target.style.borderColor = '#e5e7eb';
                e.target.style.background = 'white';
              }
            }}
          >
            <Building2 size={16} color="#6b7280" />
            <div>
              <div style={{ fontWeight: '600', color: '#1f2937' }}>
                {company.ticker}
              </div>
              <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                {company.name}
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default CompanySelector;