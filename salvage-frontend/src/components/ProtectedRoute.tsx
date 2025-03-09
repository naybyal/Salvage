import { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';
import { loginUser } from '../api/index';
import { JWTTokens } from '../types/index';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthorized, setIsAuthorized] = useState<boolean | null>(null);

  useEffect(() => {
    const verifyAuth = async () => {
      const token = localStorage.getItem('access');
      if (!token) return setIsAuthorized(false);

      try {
        const { exp } = jwtDecode(token) as { exp: number };
        if (Date.now() >= exp * 1000) {
          await refreshToken();
        } else {
          setIsAuthorized(true);
        }
      } catch (error) {
        setIsAuthorized(false);
      }
    };

    verifyAuth();
  }, []);

  const refreshToken = async (): Promise<void> => {
    const refresh = localStorage.getItem('refresh');
    if (!refresh) return setIsAuthorized(false);

    try {
      const tokens = await loginUser({
        username: 'refresh',
        password: refresh
      });
      localStorage.setItem('access', tokens.access);
      setIsAuthorized(true);
    } catch (error) {
      setIsAuthorized(false);
    }
  };

  if (isAuthorized === null) return <div>Loading...</div>;
  return isAuthorized ? children : <Navigate to="/login" replace />;
};

export default ProtectedRoute;