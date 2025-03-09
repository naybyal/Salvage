import { useNavigate } from 'react-router-dom';
import AuthForm from '../components/AuthForm';
import { loginUser } from '../api/index';
import { AuthCredentials } from '../types';

const Login: React.FC = () => {
  const navigate = useNavigate();

  const handleLogin = async (credentials: AuthCredentials) => {
    try {
      const { access, refresh } = await loginUser(credentials);
      localStorage.setItem('access', access);
      localStorage.setItem('refresh', refresh);
      navigate('/');
    } catch (error) {
      throw new Error('Invalid credentials');
    }
  };

  return (
    <AuthForm
      title="Login"
      subtitle="A sophisticated platform for efficient code writing, editing, and transpiling."
      buttonText="Login"
      alternateText="Don't have an account?"
      alternateLink="/signup"
      onSubmit={handleLogin}
    />
  );
};

export default Login;