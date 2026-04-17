import { Routes, Route, Navigate } from 'react-router-dom';
import HomePage from './pages/HomePage';
import DashboardPage from './pages/DashboardPage';
import FeaturesPage from './pages/FeaturesPage';
import LoginPage from './pages/LoginPage';
import PricingPage from './pages/PricingPage';
import ReviewPage from './pages/ReviewPage';
import SolutionsPage from './pages/SolutionsPage';
import StaffPage from './pages/StaffPage';
import TestPage from './pages/TestPage';
import TestimonialsPage from './pages/TestimonialsPage';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/features" element={<FeaturesPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/pricing" element={<PricingPage />} />
      <Route path="/review" element={<ReviewPage />} />
      <Route path="/solutions" element={<SolutionsPage />} />
      <Route path="/staff" element={<StaffPage />} />
      <Route path="/test" element={<TestPage />} />
      <Route path="/testimonials" element={<TestimonialsPage />} />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}
