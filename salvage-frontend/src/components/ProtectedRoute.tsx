import { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';
import { JWTTokens } from '../types/index';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthorized, setIsAuthorized] = useState<boolean | null>(null);
  const location = useLocation();

  useEffect(() => {
    const verifyAuth = async () => {
      const token = localStorage.getItem('access');
      if (!token) {
        setIsAuthorized(false);
        return;
      }

      try {
        const { exp } = jwtDecode(token) as { exp: number };
        if (Date.now() >= exp * 1000) {
          setIsAuthorized(false);
          localStorage.removeItem('access');
          localStorage.removeItem('refresh');
        } else {
          setIsAuthorized(true);
        }
      } catch (error) {
        setIsAuthorized(false);
      }
    };

    verifyAuth();
  }, [location.pathname]);

  if (isAuthorized === null) return <div>Loading...</div>;

  return isAuthorized ? (
    <>{children}</>
  ) : (
    <Navigate to="/login" state={{ from: location }} replace />
  );
};

export default ProtectedRoute;