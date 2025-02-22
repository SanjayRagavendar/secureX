import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

const Transactions = () => {
  const [transactions, setTransactions] = useState([]);
  const { accountId } = useParams();
  const token = localStorage.getItem("token");

  useEffect(() => {
    if (!token) return;

    const fetchTransactions = async () => {
      try {
        const response = await fetch(
          `http://192.168.137.214:5000/api/transactions/${accountId}`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
          }
        );

        if (!response.ok) {
          throw new Error("Failed to fetch transactions");
        }

        const data = await response.json();
        setTransactions(data);
      } catch (error) {
        console.error(error);
      }
    };

    fetchTransactions();
  }, [accountId, token]);

  return (
    <div className='min-h-screen bg-gray-100 py-8'>
      <div className='max-w-2xl mx-auto'>
        <h2 className='text-2xl font-bold text-gray-800 text-center mb-6'>
          Transaction History
        </h2>

        {transactions.length === 0 ? (
          <p className='text-center text-gray-500'>No transactions found.</p>
        ) : (
          <div className='space-y-4'>
            {transactions.map((transaction) => (
              <div
                key={transaction.id}
                className='bg-white p-4 rounded-lg shadow-md border-l-4 
                border-blue-500 flex justify-between items-center'
              >
                <div>
                  <p className='text-gray-700 font-medium'>
                    {transaction.transaction_type.toUpperCase()}
                  </p>
                  <p className='text-sm text-gray-500'>
                    {new Date(transaction.created_at).toLocaleString()}
                  </p>
                </div>
                <p
                  className={`text-lg font-bold ${
                    transaction.from_account_id === accountId
                      ? "text-red-500"
                      : "text-green-500"
                  }`}
                >
                  {transaction.from_account_id === accountId ? "-" : "+"}$
                  {transaction.amount}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Transactions;
