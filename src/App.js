import React, { useState } from 'react';
import './App.css';
import Layout from './components/Layout';
import CompanySelector from './components/CompanySelector';
import CreditScoreDisplay from './components/CreditScoreDisplay';
import FinancialCharts from './components/FinancialCharts';
import { calculateCreditScore } from './utils/creditScoreCalculator';
import { companies } from './data/mockData';

function App() {
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [creditScore, setCreditScore] = useState(null);

  const handleCompanySelect = (ticker) => {
    const company = companies.find(c => c.ticker === ticker);
    if (company) {
      setSelectedCompany(company);
      const score = calculateCreditScore(company);
      setCreditScore(score);
    }
  };

  return (
    <div className="App">
      <Layout>
        <div className="main-content">
          <CompanySelector 
            companies={companies}
            selectedCompany={selectedCompany}
            onCompanySelect={handleCompanySelect}
          />
          
          {selectedCompany && (
            <div className="dashboard-grid">
              <CreditScoreDisplay 
                company={selectedCompany}
                creditScore={creditScore}
              />
              <FinancialCharts 
                company={selectedCompany}
              />
            </div>
          )}
        </div>
      </Layout>
    </div>
  );
}

export default App;