import { Link, useNavigate } from "react-router-dom";

const Navbar = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <nav className='bg-gray-900 text-white p-4 flex justify-between items-center'>
      <h1 className='text-2xl font-bold'>FinTech Bank</h1>
      <div className='flex space-x-4 items-center'>
        <Link to='/' className='hover:text-gray-400'>
          Dashboard
        </Link>
        <Link to='/transactions' className='hover:text-gray-400'>
          Transactions
        </Link>
        <Link to='/transfer' className='hover:text-gray-400'>
          Transfer
        </Link>
        <button
          onClick={handleLogout}
          className='bg-red-500 px-4 py-2 rounded hover:bg-red-700'
        >
          Logout
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
