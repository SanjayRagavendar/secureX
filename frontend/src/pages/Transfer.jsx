import { useState } from "react";
import axios from "axios";

const Transfer = () => {
  const [form, setForm] = useState({
    from_account: "",
    to_account: "",
    amount: "",
  });
  const [message, setMessage] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(
        "http://192.168.64.152:5000/api/transfer",
        form,
        {
          headers: {
            Authorization: `Bearer ${sessionStorage.getItem("token")}`,
          },
        }
      );
      setMessage(res.data.message);
    } catch (err) {
      setMessage("Transfer failed");
    }
  };

  return (
    <div className='p-6'>
      <h2 className='text-2xl font-bold flex justify-center pt-2 pb-2'>
        Transfer Money
      </h2>
      <form onSubmit={handleSubmit} className='mt-4'>
        <input
          type='text'
          name='from_account'
          placeholder='From Account ID'
          onChange={handleChange}
          className='w-full p-2 border rounded mb-3'
        />
        <input
          type='text'
          name='to_account'
          placeholder='To Account ID'
          onChange={handleChange}
          className='w-full p-2 border rounded mb-3'
        />
        <input
          type='number'
          name='amount'
          placeholder='Amount'
          onChange={handleChange}
          className='w-full p-2 border rounded mb-12'
        />
        <button
          type='submit'
          className='w-full bg-gray-900 text-white p-2 rounded'
        >
          Transfer
        </button>
      </form>
      {message && <p className='mt-4'>{message}</p>}
    </div>
  );
};

export default Transfer;
