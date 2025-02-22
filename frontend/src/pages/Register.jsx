import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const Register = () => {
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post("http://192.168.64.152:5000/api/auth/register", form);
      navigate("/login");
    } catch (err) {
      setError("Registration failed");
    }
  };

  return (
    <div className='flex justify-center items-center h-screen bg-gray-100'>
      <form
        onSubmit={handleSubmit}
        className='bg-white p-6 shadow-md flex flex-col justify-center rounded-lg w-96'
      >
        <h2 className='text-xl font-bold mb-4 place-self-center'>Register</h2>
        {error && <p className='text-red-500'>{error}</p>}
        <input
          type='text'
          name='username'
          placeholder='Username'
          onChange={handleChange}
          className='w-full p-2 border rounded mb-3'
        />
        <input
          type='email'
          name='email'
          placeholder='Email'
          onChange={handleChange}
          className='w-full p-2 border rounded mb-3'
        />
        <input
          type='password'
          name='password'
          placeholder='Password'
          onChange={handleChange}
          className='w-full p-2 border rounded mb-3'
        />
        <button
          type='submit'
          className='w-full bg-gray-900 text-white p-2 rounded'
        >
          Register
        </button>
        <div className='flex justify-center space-x-1 pt-2'>
          Have an account already ? <nbsp />
          <button
            onClick={() => navigate("/login")}
            className='text-blue-600 hover:underline'
          >
            Login
          </button>
        </div>
      </form>
    </div>
  );
};

export default Register;
