import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Header from './components/header.jsx';
//import EventList from './pages/EventList';
//import EventDetail from './pages/EventDetail';
import Login from './pages/Login';
import { AuthProvider } from './context/AuthContext';
import PrivateRoute from './components/PrivateRoute.jsx';
//import CreateEvent from './pages/CreateEvent';
//import Unauthorized from './pages/Unauthorized';
//import Attendees from './components/Attendees';
import Register from './pages/Register';

export default function App() {
  return (
    <Router>
      <AuthProvider>
        <Header />

        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

        </Routes>
      </AuthProvider>
    </Router>
  );
}

