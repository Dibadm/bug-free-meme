import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import { ArrowDownToLine, ArrowUpFromLine, ArrowLeftRight, Search, Trophy, Info } from "lucide-react";
import { useTransactions, useWalletBalance, useCreateDeposit, useCreateWithdrawal } from "@/lib/queries";
import { usePaymentSettings } from "@/lib/paymentQueries";
import { useAuth } from "@/lib/useAuth";
import { useHaptics } from "@/hooks";
import { useToast } from "@/components/Toast";
import {
  TopNav,
  PageContainer,
  Button,
  Badge,
  Tabs,
  EmptyState,
  Sheet,
  Input,
  Skeleton,
} from "@/components";

type FilterTab = "all" | "deposit" | "withdrawal" | "transfer" | "prize";

export default function WalletPage() {
  const [activeTab, setActiveTab] = useState<FilterTab>("all");
  const [showDepositSheet, setShowDepositSheet] = useState(false);
  const [showWithdrawSheet, setShowWithdrawSheet] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const { user } = useAuth();
  const balanceQuery = useWalletBalance();
  const transactionsQuery = useTransactions();
  const paymentSettingsQuery = usePaymentSettings();
  const haptics = useHaptics();

  const balance = balanceQuery.data?.balance || user?.balance || 0;
  const transactions = transactionsQuery.data || [];
  const paymentSettings = paymentSettingsQuery.data;

  const filteredTransactions = useMemo(() => {
    let filtered = transactions;
    if (activeTab !== "all") {
      filtered = filtered.filter((t: any) => t.type === activeTab);
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      filtered = filtered.filter((t: any) => (t.description || t.title || "").toLowerCase().includes(q));
    }
    return filtered;
  }, [transactions, activeTab, searchQuery]);

  const tabs = [
    { id: "all", label: "All" },
    { id: "deposit", label: "Deposits" },
    { id: "withdrawal", label: "Withdrawals" },
    { id: "transfer", label: "Transfers" },
    { id: "prize", label: "Prizes" },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "success";
      case "pending":
        return "warning";
      case "failed":
        return "danger";
      default:
        return "default";
    }
  };

  return (
    <PageContainer>
      <TopNav title="Wallet" />

      <div className="p-4 space-y-5">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="bg-gradient-to-br from-habesha-surface/90 via-habesha-surface/80 to-habesha-surface/70 backdrop-blur-xl border border-white/10 rounded-3xl p-6 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-habesha-gold/10 to-transparent pointer-events-none" />
              <div className="relative z-10 space-y-4">
                <div>
                  <p className="text-xs text-white/60 uppercase tracking-wider">Total Balance</p>
                  <p className="text-3xl font-bold text-white mt-1">ETB {balance.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
                </div>
                {paymentSettings?.maintenance_message && (
                  <div className="flex items-center gap-2 p-3 bg-habesha-gold/10 border border-habesha-gold/30 rounded-2xl">
                    <Info className="h-4 w-4 text-habesha-gold" />
                    <p className="text-xs text-habesha-gold">{paymentSettings.maintenance_message}</p>
                  </div>
                )}
                <div className="flex gap-2">
                  <Button size="sm" onClick={() => { haptics.light(); setShowDepositSheet(true); }} className="flex-1" disabled={paymentSettings?.is_deposit_enabled === false}>
                    <ArrowDownToLine className="h-4 w-4 mr-1.5" />
                    Deposit
                  </Button>
                  <Button variant="secondary" size="sm" onClick={() => { haptics.light(); setShowWithdrawSheet(true); }} className="flex-1">
                    <ArrowUpFromLine className="h-4 w-4 mr-1.5" />
                    Withdraw
                  </Button>
                </div>
              </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="space-y-3">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-white/40" />
            <input
              type="text"
              placeholder="Search transactions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-11 pr-4 py-3 bg-habesha-surface-light border border-white/10 rounded-2xl text-white placeholder-white/40 focus:outline-none focus:border-habesha-gold/50 transition-colors"
            />
          </div>
          <Tabs tabs={tabs} activeTab={activeTab} onChange={(id) => setActiveTab(id as FilterTab)} />
        </motion.div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }} className="space-y-2">
          {transactionsQuery.isLoading ? (
            Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-16 rounded-2xl" />)
          ) : filteredTransactions.length === 0 ? (
            <EmptyState
              icon={<ArrowLeftRight className="h-12 w-12" />}
              title="No transactions yet"
              description="Your transaction history will appear here"
              actionLabel="Make a Deposit"
              onAction={() => setShowDepositSheet(true)}
            />
          ) : (
            filteredTransactions.map((tx: any) => (
              <motion.div
                key={tx.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="bg-habesha-surface/80 border border-white/10 rounded-2xl p-4 flex items-center justify-between"
              >
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-2xl bg-habesha-surface-light flex items-center justify-center">
                    {tx.type === "deposit" && <ArrowDownToLine className="h-5 w-5 text-habesha-green" />}
                    {tx.type === "withdrawal" && <ArrowUpFromLine className="h-5 w-5 text-red-400" />}
                    {tx.type === "transfer" && <ArrowLeftRight className="h-5 w-5 text-blue-400" />}
                    {tx.type === "prize" && <Trophy className="h-5 w-5 text-habesha-gold" />}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-white">{tx.description || tx.title || tx.type}</p>
                    <p className="text-xs text-white/60">{new Date(tx.created_at || tx.date).toLocaleDateString()}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`text-sm font-bold ${tx.type === "deposit" || tx.type === "prize" ? "text-habesha-green" : "text-red-400"}`}>
                    {tx.type === "deposit" || tx.type === "prize" ? "+" : "-"}ETB {Math.abs(tx.amount || 0).toFixed(2)}
                  </p>
                  <Badge variant={getStatusColor(tx.status)} className="text-[10px] px-1.5 py-0.5">
                    {tx.status || "pending"}
                  </Badge>
                </div>
              </motion.div>
            ))
          )}
        </motion.div>

        <div className="h-6" />
      </div>

      <Sheet isOpen={showDepositSheet} onClose={() => setShowDepositSheet(false)} title="Deposit">
        <DepositForm onClose={() => setShowDepositSheet(false)} />
      </Sheet>

      <Sheet isOpen={showWithdrawSheet} onClose={() => setShowWithdrawSheet(false)} title="Withdraw">
        <WithdrawForm balance={balance} onClose={() => setShowWithdrawSheet(false)} />
      </Sheet>
    </PageContainer>
  );
}

function DepositForm({ onClose }: { onClose: () => void }) {
  const [amount, setAmount] = useState("");
  const [smsCode, setSmsCode] = useState("");
  const [mode, setMode] = useState<"sms" | "proof">("sms");
  const haptics = useHaptics();
  const toast = useToast();
  const createDeposit = useCreateDeposit();
  const { data: settings } = usePaymentSettings();

  const handleSubmit = () => {
    haptics.medium();
    const parsed = parseFloat(amount);
    if (!parsed || parsed <= 0) {
      toast("Please enter a valid amount", "error");
      return;
    }
    if (settings && (parsed < settings.min_deposit || parsed > settings.max_deposit)) {
      toast(`Amount must be between ${settings.min_deposit} and ${settings.max_deposit} ETB`, "error");
      return;
    }
    if (mode === "sms") {
      if (!smsCode.trim()) {
        toast("Please paste the SMS confirmation code", "error");
        return;
      }
      createDeposit.mutate({ amount: parsed, smsCode: smsCode.trim() }, {
        onSuccess: onClose,
      });
    } else {
      createDeposit.mutate({ amount: parsed, proofUrl: "https://example.com/proof.jpg" }, {
        onSuccess: onClose,
      });
    }
  };

  return (
    <div className="space-y-4">
      {settings && (
        <div className="p-4 bg-habesha-surface-light border border-white/10 rounded-2xl space-y-2">
          <p className="text-xs text-white/60 uppercase tracking-wider">Telebirr Details</p>
          <div className="flex justify-between text-sm">
            <span className="text-white/60">Number:</span>
            <span className="text-white font-medium">{settings.telebirr_number}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-white/60">Account:</span>
            <span className="text-white font-medium">{settings.account_holder_name}</span>
          </div>
          <p className="text-xs text-white/60 pt-1">{settings.deposit_instructions}</p>
        </div>
      )}
      <div className="flex gap-2 p-1 bg-habesha-surface-light rounded-xl">
        <button
          onClick={() => setMode("sms")}
          className={`flex-1 py-2 text-sm rounded-lg transition-colors ${mode === "sms" ? "bg-habesha-gold text-black font-medium" : "text-white/60 hover:text-white"}`}
        >
          SMS Verification
        </button>
        <button
          onClick={() => setMode("proof")}
          className={`flex-1 py-2 text-sm rounded-lg transition-colors ${mode === "proof" ? "bg-habesha-gold text-black font-medium" : "text-white/60 hover:text-white"}`}
        >
          Manual Proof
        </button>
      </div>
      <Input label="Amount (ETB)" type="number" value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="100" />
      {mode === "sms" ? (
        <div className="space-y-2">
          <p className="text-xs text-white/60">Send money to the Telebirr number above, then paste the SMS confirmation below.</p>
          <Input label="SMS Confirmation" value={smsCode} onChange={(e) => setSmsCode(e.target.value)} placeholder="Paste SMS text here..." />
        </div>
      ) : (
        <Input label="Payment Proof URL" value="" onChange={() => {}} placeholder="https://..." />
      )}
      {settings && (
        <p className="text-xs text-white/40">
          Limits: ETB {settings.min_deposit} - ETB {settings.max_deposit}
        </p>
      )}
      <Button onClick={handleSubmit} loading={createDeposit.isPending} className="w-full" disabled={settings?.is_deposit_enabled === false}>
        {settings?.is_deposit_enabled === false ? "Deposits Disabled" : "Submit Deposit"}
      </Button>
    </div>
  );
}

function WithdrawForm({ balance, onClose }: { balance: number; onClose: () => void }) {
  const [amount, setAmount] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const haptics = useHaptics();
  const toast = useToast();
  const createWithdrawal = useCreateWithdrawal();

  const handleSubmit = () => {
    haptics.medium();
    const parsed = parseFloat(amount);
    if (!parsed || parsed <= 0) {
      toast("Please enter a valid amount", "error");
      return;
    }
    if (parsed > balance) {
      toast("Insufficient balance", "error");
      return;
    }
    createWithdrawal.mutate({ amount: parsed, phoneNumber }, {
      onSuccess: onClose,
    });
  };

  return (
    <div className="space-y-4">
      <Input label="Amount (ETB)" type="number" value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="100" />
      <Input label="Phone Number" value={phoneNumber} onChange={(e) => setPhoneNumber(e.target.value)} placeholder="+251..." />
      <p className="text-xs text-white/60">Available balance: ETB {balance.toFixed(2)}</p>
      <Button onClick={handleSubmit} loading={createWithdrawal.isPending} className="w-full">
        Request Withdrawal
      </Button>
    </div>
  );
}
