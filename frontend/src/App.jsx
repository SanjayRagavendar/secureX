import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  useLocation,
} from "react-router-dom";
import { useState, useEffect } from "react";
import { jwtDecode } from "jwt-decode";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Transactions from "./pages/Transactions";
import Transfer from "./pages/Transfer";
import Navbar from "./components/Navbar";

const App = () => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const checkToken = () => {
      const token = sessionStorage.getItem("token");
      if (token) {
        const decoded = jwtDecode(token);
        setUser(decoded);
      } else {
        setUser(null);
      }
    };

    checkToken();
    window.addEventListener("storage", checkToken);
    return () => window.removeEventListener("storage", checkToken);
  }, []);

  return (
    <Router>
      <Layout user={user}>
        <Routes>
          <Route
            path='/'
            element={user ? <Dashboard /> : <Navigate to='/login' />}
          />
          <Route path='/login' element={<Login setUser={setUser} />} />
          <Route path='/register' element={<Register />} />
          <Route
            path='/transactions'
            element={user ? <Transactions /> : <Navigate to='/login' />}
          />
          <Route
            path='/transfer'
            element={user ? <Transfer /> : <Navigate to='/login' />}
          />
        </Routes>
      </Layout>
    </Router>
  );
};

// ✅ Layout Component to Conditionally Show Navbar
const Layout = ({ user, children }) => {
  const location = useLocation();
  const hideNavbar = ["/login", "/register"].includes(location.pathname);

  return (
    <>
      <div className='flex justify-center'>
        <div className='lg:w-[80%] lg:h-[80%] md:w-[100%] md:h-[100%]'>
          {!hideNavbar && user && <Navbar />}
          {children}
        </div>
      </div>
    </>
  );
};

export default App;
