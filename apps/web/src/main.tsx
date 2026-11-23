import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './index.css';
import './workbench/core.css';
import './workbench/experience.css';
import './workbench/voice.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);

import './workbench/business.css';
import './workbench/inventory.css';
import './workbench/planning.css';

import './workbench/operations.css';

import './workbench/support.css';
import './workbench/polish.css';
document.documentElement.dataset.motion=localStorage.getItem('shongoti_motion')||'system';
