import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/useAuth.js';

export default function PrivateRoute({ children, allowedRoles }) {
  const { user } = useAuth();

  // Not logged in
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Role not allowed
  if (allowedRoles && !allowedRoles.includes(user?.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  // Access granted
  return children;
}
