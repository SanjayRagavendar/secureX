import { useEffect, useState } from "react";
import axios from "axios";

const Dashboard = () => {
  const [accounts, setAccounts] = useState([]);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [accountType, setAccountType] = useState("");
  const [balance, setBalance] = useState("");
  const [loading, setLoading] = useState(false);

  // ✅ Fetch accounts when the page loads
  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      const token = sessionStorage.getItem("token");
      if (!token) {
        setError("Unauthorized: No token found");
        return;
      }

      const res = await axios.get("http://192.168.137.214:5000/api/accounts", {
        headers: { Authorization: `Bearer ${token}` },
      });

      setAccounts(res.data);
      setError("");
    } catch (err) {
      setError("Failed to fetch accounts");
      console.error(err);
    }
  };

  // ✅ Create a new account
  const createAccount = async () => {
    if (!accountType) {
      setError("Please select an account type");
      return;
    }

    setLoading(true);
    try {
      const token = sessionStorage.getItem("token");
      if (!token) {
        setError("Unauthorized: No token found");
        setLoading(false);
        return;
      }

      const res = await axios.post(
        "http://192.168.137.214:5000/api/accounts",
        {
          account_type: accountType,
          initial_balance: balance || 0,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      setAccounts([...accounts, res.data]); // ✅ Add new account to list
      setAccountType("");
      setBalance("");
      setShowForm(false); // ✅ Hide form after creation
      setError("");
    } catch (err) {
      setError("Failed to create account");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className='p-6 bg-white h-screen shadow-md rounded-lg'>
      <div className='flex justify-between items-center mb-4'>
        <h2 className='text-xl font-bold'>Your Accounts</h2>
        {/* ✅ Push "Create Account" button to the right */}
        <button
          onClick={() => setShowForm(!showForm)}
          className='bg-gray-900 text-white px-4 py-2 rounded'
        >
          {showForm ? "Cancel" : "Create Account"}
        </button>
      </div>

      {error && <p className='text-red-500'>{error}</p>}

      {/* ✅ Show Form Only When Button is Clicked */}
      {showForm && (
        <div className='mb-4 border p-4 rounded bg-gray-100'>
          <select
            className='border p-2 rounded w-full mb-2'
            value={accountType}
            onChange={(e) => setAccountType(e.target.value)}
          >
            <option value=''>Select Account Type</option>
            <option value='Current'>Current</option>
            <option value='Savings'>Savings</option>
          </select>
          <input
            type='number'
            className='border p-2 rounded w-full mb-2'
            placeholder='Initial Balance (optional)'
            value={balance}
            onChange={(e) => setBalance(e.target.value)}
          />
          <button
            onClick={createAccount}
            className='bg-green-500 text-white p-2 w-full rounded'
            disabled={loading}
          >
            {loading ? "Creating..." : "Confirm"}
          </button>
        </div>
      )}

      {/* ✅ List User's Accounts */}
      <div className='grid grid-cols-3 gap-4'>
        {accounts.length === 0 ? (
          <p className='text-gray-500'>No accounts found</p>
        ) : (
          accounts.map((acc) => (
            <div
              key={acc.id}
              className='border p-4 rounded-lg bg-gray-50 shadow-md'
            >
              <p className='text-gray-600 text-xl pb-3'>
                Account No: <strong>{acc.account_number}</strong>
              </p>
              <p className='text-gray-700'>
                Type: <strong>{acc.account_type}</strong>
              </p>
              <p className='text-gray-900 font-semibold'>
                Balance: ₹{acc.balance.toFixed(2)}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Dashboard;
