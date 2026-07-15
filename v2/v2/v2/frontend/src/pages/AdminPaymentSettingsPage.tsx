import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Settings, Save } from "lucide-react";
import { useAdminPaymentSettings, useUpdatePaymentSettings } from "@/lib/paymentQueries";
import { useToast } from "@/components/Toast";
import { PageContainer, Button, Input, Skeleton } from "@/components";

export default function AdminPaymentSettingsPage() {
  const { data: settings, isLoading } = useAdminPaymentSettings();
  const updateMutation = useUpdatePaymentSettings();
  const toast = useToast();

  const [form, setForm] = useState({
    telebirr_number: "",
    account_holder_name: "",
    deposit_instructions: "",
    min_deposit: "",
    max_deposit: "",
    is_deposit_enabled: true,
    auto_credit_enabled: false,
    maintenance_message: "",
    is_active: true,
  });

  useEffect(() => {
    if (settings) {
      setForm({
        telebirr_number: settings.telebirr_number || "",
        account_holder_name: settings.account_holder_name || "",
        deposit_instructions: settings.deposit_instructions || "",
        min_deposit: settings.min_deposit?.toString() || "",
        max_deposit: settings.max_deposit?.toString() || "",
        is_deposit_enabled: settings.is_deposit_enabled ?? true,
        auto_credit_enabled: settings.auto_credit_enabled ?? false,
        maintenance_message: settings.maintenance_message || "",
        is_active: settings.is_active ?? true,
      });
    }
  }, [settings]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateMutation.mutate(
      {
        telebirr_number: form.telebirr_number,
        account_holder_name: form.account_holder_name,
        deposit_instructions: form.deposit_instructions,
        min_deposit: parseFloat(form.min_deposit),
        max_deposit: parseFloat(form.max_deposit),
        is_deposit_enabled: form.is_deposit_enabled,
        auto_credit_enabled: form.auto_credit_enabled,
        maintenance_message: form.maintenance_message || null,
        is_active: form.is_active,
      },
      {
        onSuccess: () => {
          toast("Payment settings saved successfully", "success");
        },
        onError: () => {
          toast("Failed to save payment settings", "error");
        },
      }
    );
  };

  if (isLoading) {
    return (
      <PageContainer>
        <div className="p-4 space-y-4">
          <Skeleton className="h-8 w-48 rounded-3xl" />
          <Skeleton className="h-64 rounded-3xl" />
        </div>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <div className="p-4 space-y-5">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-2xl bg-habesha-gold/20 flex items-center justify-center">
            <Settings className="h-5 w-5 text-habesha-gold" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Payment Settings</h1>
            <p className="text-xs text-white/60">Configure Telebirr deposit settings</p>
          </div>
        </motion.div>

        <motion.form initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} onSubmit={handleSubmit} className="space-y-4">
          <div className="bg-habesha-surface/80 border border-white/10 rounded-3xl p-5 space-y-4">
            <div className="space-y-3">
              <Input
                label="Telebirr Number"
                value={form.telebirr_number}
                onChange={(e) => setForm({ ...form, telebirr_number: e.target.value })}
                placeholder="+2519xxxxxxxx"
                required
              />
              <Input
                label="Account Holder Name"
                value={form.account_holder_name}
                onChange={(e) => setForm({ ...form, account_holder_name: e.target.value })}
                placeholder="John Doe"
                required
              />
              <div>
                <label className="block text-xs text-white/60 mb-1.5">Deposit Instructions</label>
                <textarea
                  value={form.deposit_instructions}
                  onChange={(e) => setForm({ ...form, deposit_instructions: e.target.value })}
                  placeholder="Send money to the Telebirr number..."
                  className="w-full px-4 py-3 bg-habesha-surface-light border border-white/10 rounded-2xl text-white placeholder-white/40 focus:outline-none focus:border-habesha-gold/50 transition-colors resize-none"
                  rows={3}
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <Input
                  label="Minimum Deposit (ETB)"
                  type="number"
                  value={form.min_deposit}
                  onChange={(e) => setForm({ ...form, min_deposit: e.target.value })}
                  placeholder="10"
                  required
                />
                <Input
                  label="Maximum Deposit (ETB)"
                  type="number"
                  value={form.max_deposit}
                  onChange={(e) => setForm({ ...form, max_deposit: e.target.value })}
                  placeholder="10000"
                  required
                />
              </div>
              <div className="space-y-2">
                <label className="block text-xs text-white/60">Maintenance Message</label>
                <input
                  type="text"
                  value={form.maintenance_message}
                  onChange={(e) => setForm({ ...form, maintenance_message: e.target.value })}
                  placeholder="Deposits are temporarily unavailable..."
                  className="w-full px-4 py-3 bg-habesha-surface-light border border-white/10 rounded-2xl text-white placeholder-white/40 focus:outline-none focus:border-habesha-gold/50 transition-colors"
                />
              </div>
            </div>
          </div>

          <div className="bg-habesha-surface/80 border border-white/10 rounded-3xl p-5 space-y-3">
            <h3 className="text-sm font-medium text-white">Settings</h3>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-white">Deposit Enabled</p>
                <p className="text-xs text-white/60">Allow new deposits</p>
              </div>
              <button
                type="button"
                onClick={() => setForm({ ...form, is_deposit_enabled: !form.is_deposit_enabled })}
                className={`w-12 h-7 rounded-full transition-colors ${form.is_deposit_enabled ? "bg-habesha-green" : "bg-white/20"}`}
              >
                <div className={`w-5 h-5 rounded-full bg-white shadow transition-transform ${form.is_deposit_enabled ? "translate-x-6" : "translate-x-1"}`} />
              </button>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-white">Auto Credit</p>
                <p className="text-xs text-white/60">Automatically credit wallet after SMS verification</p>
              </div>
              <button
                type="button"
                onClick={() => setForm({ ...form, auto_credit_enabled: !form.auto_credit_enabled })}
                className={`w-12 h-7 rounded-full transition-colors ${form.auto_credit_enabled ? "bg-habesha-green" : "bg-white/20"}`}
              >
                <div className={`w-5 h-5 rounded-full bg-white shadow transition-transform ${form.auto_credit_enabled ? "translate-x-6" : "translate-x-1"}`} />
              </button>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-white">Active</p>
                <p className="text-xs text-white/60">Use this as the active payment configuration</p>
              </div>
              <button
                type="button"
                onClick={() => setForm({ ...form, is_active: !form.is_active })}
                className={`w-12 h-7 rounded-full transition-colors ${form.is_active ? "bg-habesha-green" : "bg-white/20"}`}
              >
                <div className={`w-5 h-5 rounded-full bg-white shadow transition-transform ${form.is_active ? "translate-x-6" : "translate-x-1"}`} />
              </button>
            </div>
          </div>

          <Button type="submit" loading={updateMutation.isPending} className="w-full">
            <Save className="h-4 w-4 mr-2" />
            Save Settings
          </Button>
        </motion.form>
      </div>
    </PageContainer>
  );
}
