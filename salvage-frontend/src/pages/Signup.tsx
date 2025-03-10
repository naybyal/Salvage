import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import AuthForm from '../components/AuthForm';
import { registerUser } from '../api';
import { AuthCredentials } from '../types';

const Signup: React.FC = () => {
  const navigate = useNavigate();

  const handleSignup = async (credentials: AuthCredentials) => {
    try {
      await registerUser(credentials);
      navigate('/login');
    } catch (error) {
      throw new Error('Registration failed');
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
        title="Get Started"
        subtitle="Create your account to begin transpiling"
        buttonText="Create Account"
        alternateText="Already have an account?"
        alternateLink="/login"
        onSubmit={handleSignup}
      />
    </motion.div>
  );
};

export default Signup;