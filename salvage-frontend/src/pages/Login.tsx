import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import AuthForm from '../components/AuthForm';
import { loginUser } from '../api';
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
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="min-h-screen bg-gray-900 flex items-center justify-center p-4"
    >
      <AuthForm
        title="Welcome Back"
        subtitle="Continue your code transformation journey"
        buttonText="Sign In"
        alternateText="New here?"
        alternateLink="/signup"
        onSubmit={handleLogin}
      />
    </motion.div>
  );
};

export default Login;