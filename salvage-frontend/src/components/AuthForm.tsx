import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { AuthCredentials } from '../types';

interface AuthFormProps {
  title: string;
  subtitle: string;
  buttonText: string;
  alternateText: string;
  alternateLink: string;
  onSubmit: (credentials: AuthCredentials) => Promise<void>;
}

const AuthForm: React.FC<AuthFormProps> = ({
  title,
  subtitle,
  buttonText,
  alternateText,
  alternateLink,
  onSubmit
}) => {
  const [credentials, setCredentials] = useState<AuthCredentials>({
    username: '',
    password: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await onSubmit(credentials);
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Authentication failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md space-y-8">
      <motion.div
        initial={{ y: 20 }}
        animate={{ y: 0 }}
        className="text-center"
      >
        <div className="mb-8 flex justify-center">
          <div className="w-16 h-16 bg-red-600 rounded-2xl flex items-center justify-center">
            <svg
              className="w-8 h-8 text-red-200 transform rotate-45"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M14 5l7 7m0 0l-7 7m7-7H3"
              />
            </svg>
          </div>
        </div>

        <motion.h1
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-4xl font-bold bg-gradient-to-r from-red-400 to-orange-400 bg-clip-text text-transparent mb-2"
        >
          {title}
        </motion.h1>
        <p className="text-gray-400 text-lg">{subtitle}</p>
      </motion.div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Username
            </label>
            <input
              type="text"
              value={credentials.username}
              onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
              className="w-full px-4 py-3 bg-gray-800 border-2 border-gray-700 rounded-lg text-white
                        focus:border-red-500 focus:ring-2 focus:ring-red-500/30 outline-none transition-all"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Password
            </label>
            <input
              type="password"
              value={credentials.password}
              onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
              className="w-full px-4 py-3 bg-gray-800 border-2 border-gray-700 rounded-lg text-white
                        focus:border-red-500 focus:ring-2 focus:ring-red-500/30 outline-none transition-all"
              required
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-3 px-6 bg-red-600 hover:bg-red-700 rounded-lg font-medium text-white
                    relative overflow-hidden transition-all disabled:opacity-50"
        >
          {isLoading ? (
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
            </div>
          ) : (
            buttonText
          )}
        </button>
      </form>

      <div className="text-center text-gray-400">
        {alternateText}{' '}
        <button
          onClick={() => navigate(alternateLink)}
          className="text-red-400 hover:text-red-300 underline underline-offset-4 transition-colors"
        >
          {alternateLink === '/signup' ? 'Create account' : 'Sign in instead'}
        </button>
      </div>
    </div>
  );
};

export default AuthForm;