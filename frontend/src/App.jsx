import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import ActivitiesList from './pages/ActivitiesList';
import ActivityForm from './pages/ActivityForm';
import ActivityDetail from './pages/ActivityDetail';
import AreasList from './pages/AreasList';
import Reports from './pages/Reports';
import EipdWizard from './pages/EipdWizard';
import BrechasList from './pages/BrechasList';
import ArsopList from './pages/ArsopList';
import './App.css';

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/actividades" element={<ActivitiesList />} />
          <Route path="/actividades/nueva" element={<ActivityForm />} />
          <Route path="/actividades/:id" element={<ActivityDetail />} />
          <Route path="/actividades/:id/editar" element={<ActivityForm />} />
          <Route path="/actividades/:id/eipd" element={<EipdWizard />} />
          <Route path="/brechas" element={<BrechasList />} />
          <Route path="/arsop" element={<ArsopList />} />
          <Route path="/areas" element={<AreasList />} />
          <Route path="/reportes" element={<Reports />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
