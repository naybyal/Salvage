import { useNavigate } from 'react-router-dom';
import AuthForm from '../components/AuthForm';
import { registerUser } from '../api/index';
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
    <AuthForm
      title="Sign Up"
      subtitle="Create your account to start transpiling code efficiently."
      buttonText="Create Account"
      alternateText="Already have an account?"
      alternateLink="/login"
      onSubmit={handleSignup}
    />
  );
};

export default Signup;