import React, { useState } from "react";
import { ArrowLeftRight, ChevronDown, AlertCircle } from "lucide-react";
import { toast } from "react-hot-toast";

const TransferMoney = () => {
  const [transferDetails, setTransferDetails] = useState({
    fromAccount: "",
    toAccount: "",
    amount: "",
    description: "",
  });
  const [loading, setLoading] = useState(false);

  const [accounts] = useState([
    { id: 1, type: "Checking", number: "****4321", balance: 5000 },
    { id: 2, type: "Savings", number: "****8765", balance: 12000 },
  ]);

  const handleTransfer = async (e) => {
    e.preventDefault();
    if (
      !transferDetails.fromAccount ||
      !transferDetails.toAccount ||
      !transferDetails.amount
    ) {
      toast.error("Please fill in all required fields");
      return;
    }
    if (transferDetails.fromAccount === transferDetails.toAccount) {
      toast.error("Cannot transfer to the same account");
      return;
    }
    if (transferDetails.amount <= 0) {
      toast.error("Amount must be greater than zero");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch("/api/transfer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(transferDetails),
      });
      const data = await response.json();
      if (response.ok) {
        toast.success("Transfer successful!");
        setTransferDetails({
          fromAccount: "",
          toAccount: "",
          amount: "",
          description: "",
        });
      } else {
        toast.error(data.message || "Transfer failed");
      }
    } catch (error) {
      toast.error("Something went wrong. Please try again.");
    }
    setLoading(false);
  };

  return (
    <div className='min-h-screen bg-gray-50 py-12'>
      <div className='max-w-3xl mx-auto px-4 sm:px-6 lg:px-8'>
        <div className='bg-white rounded-xl shadow-lg p-8'>
          <div className='flex items-center justify-between mb-8'>
            <h1 className='text-2xl font-bold text-gray-800'>Transfer Money</h1>
            <div className='p-2 bg-blue-100 rounded-lg'>
              <ArrowLeftRight className='w-6 h-6 text-blue-600' />
            </div>
          </div>

          <form className='space-y-6' onSubmit={handleTransfer}>
            <div>
              <label className='block text-gray-700 mb-2'>From Account</label>
              <div className='relative'>
                <select
                  className='w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500'
                  value={transferDetails.fromAccount}
                  onChange={(e) =>
                    setTransferDetails({
                      ...transferDetails,
                      fromAccount: e.target.value,
                    })
                  }
                >
                  <option value=''>Select account</option>
                  {accounts.map((account) => (
                    <option key={account.id} value={account.id}>
                      {account.type} - {account.number} (${account.balance})
                    </option>
                  ))}
                </select>
                <ChevronDown className='w-5 h-5 text-gray-400 absolute right-3 top-3.5' />
              </div>
            </div>

            <div>
              <label className='block text-gray-700 mb-2'>To Account</label>
              <div className='relative'>
                <select
                  className='w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500'
                  value={transferDetails.toAccount}
                  onChange={(e) =>
                    setTransferDetails({
                      ...transferDetails,
                      toAccount: e.target.value,
                    })
                  }
                >
                  <option value=''>Select account</option>
                  {accounts.map((account) => (
                    <option key={account.id} value={account.id}>
                      {account.type} - {account.number}
                    </option>
                  ))}
                </select>
                <ChevronDown className='w-5 h-5 text-gray-400 absolute right-3 top-3.5' />
              </div>
            </div>

            <div>
              <label className='block text-gray-700 mb-2'>Amount</label>
              <input
                type='number'
                className='w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500'
                placeholder='0.00'
                value={transferDetails.amount}
                onChange={(e) =>
                  setTransferDetails({
                    ...transferDetails,
                    amount: e.target.value,
                  })
                }
              />
            </div>

            <div>
              <label className='block text-gray-700 mb-2'>Description</label>
              <input
                type='text'
                className='w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500'
                placeholder='Add a note'
                value={transferDetails.description}
                onChange={(e) =>
                  setTransferDetails({
                    ...transferDetails,
                    description: e.target.value,
                  })
                }
              />
            </div>

            <div className='bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start space-x-3'>
              <AlertCircle className='w-5 h-5 text-yellow-600 mt-0.5' />
              <p className='text-sm text-yellow-800'>
                Please verify all details before confirming the transfer. This
                action cannot be undone.
              </p>
            </div>

            <button
              type='submit'
              disabled={loading}
              className='w-full py-3 px-4 border rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
            >
              {loading ? "Processing..." : "Confirm Transfer"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default TransferMoney;
