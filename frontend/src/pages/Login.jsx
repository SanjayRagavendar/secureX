import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { jwtDecode } from "jwt-decode";

const Login = ({ setUser }) => {
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(
        "http://192.168.137.214:5000/api/auth/login",
        form
      );
      const token = res.data.token;

      sessionStorage.setItem("token", token); // ✅ Store token

      const user = jwtDecode(token);
      setUser(user); // ✅ Update user state

      navigate("/"); // ✅ Navigate to dashboard
    } catch (err) {
      setError("Invalid Credentials");
    }
  };

  return (
    <div className='flex justify-center items-center h-screen bg-gray-100'>
      <div className='bg-white p-6 shadow-md rounded-lg w-96 relative'>
        {/* Sign Up Link */}
        <div className='flex flex-col justify-evenly pb-2'>
          <h2 className='text-xl font-bold mb-4 text-center'>Login</h2>
        </div>

        {error && <p className='text-red-500 text-sm text-center'>{error}</p>}

        <form onSubmit={handleSubmit} className='space-y-4'>
          <input
            type='email'
            name='email'
            placeholder='Email'
            onChange={handleChange}
            className='w-full p-2 border rounded'
            required
          />
          <input
            type='password'
            name='password'
            placeholder='Password'
            onChange={handleChange}
            className='w-full p-2 border rounded'
            required
          />
          <button
            type='submit'
            className='w-full bg-gray-900 text-white p-2 rounded hover:bg-gray-800 transition'
          >
            Login
          </button>
          <div className='flex justify-center space-x-1'>
            Don't have an account ? <nbsp />
            <button
              onClick={() => navigate("/register")}
              className='text-blue-600 hover:underline'
            >
              Sign Up
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;
