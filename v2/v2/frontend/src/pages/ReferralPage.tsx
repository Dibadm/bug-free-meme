import { motion } from "framer-motion";
import { Copy, Share2, Users, Gift } from "lucide-react";
import { useReferrals } from "@/lib/queries";
import { useAuth } from "@/lib/useAuth";
import { useHaptics } from "@/hooks";
import { useToast } from "@/components/Toast";
import { TopNav, PageContainer, Button, StatCard, Skeleton, EmptyState, Avatar } from "@/components";

export default function ReferralPage() {
  const { user } = useAuth();
  const referralsQuery = useReferrals();
  const haptics = useHaptics();
  const toast = useToast();

  const referrals = referralsQuery.data?.referrals || [];
  const totalEarned = referralsQuery.data?.total_earned || 0;
  const referralCode = (user as any)?.referral_code || "HABESHA123";

  const handleCopy = () => {
    haptics.light();
    navigator.clipboard.writeText(referralCode);
    toast("Referral code copied!", "success");
  };

  const handleShare = async () => {
    haptics.medium();
    const text = `Join Habesha Bet and use my referral code ${referralCode} to get started!`;
    if (navigator.share) {
      try {
        await navigator.share({ title: "Join Habesha Bet", text });
      } catch {
        // ignore share errors
      }
    } else {
      navigator.clipboard.writeText(text);
      toast("Referral link copied!", "success");
    }
  };

  return (
    <PageContainer>
      <TopNav title="Referral Dashboard" />

      <div className="p-4 space-y-5">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
          <div className="bg-gradient-to-br from-habesha-surface/90 via-habesha-surface/80 to-habesha-surface/70 backdrop-blur-xl border border-white/10 rounded-3xl p-6 text-center relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-habesha-gold/10 to-transparent pointer-events-none" />
            <div className="relative z-10 space-y-4">
              <div className="h-14 w-14 rounded-full bg-habesha-gold/10 flex items-center justify-center mx-auto">
                <Gift className="h-7 w-7 text-habesha-gold" />
              </div>
              <div>
                <p className="text-xs text-white/60 uppercase tracking-wider mb-1">Your Referral Code</p>
                <p className="text-2xl font-mono font-bold text-habesha-gold tracking-widest">{referralCode}</p>
              </div>
              <div className="flex gap-2">
                <Button variant="secondary" onClick={handleCopy} className="flex-1">
                  <Copy className="h-4 w-4 mr-2" />
                  Copy
                </Button>
                <Button onClick={handleShare} className="flex-1">
                  <Share2 className="h-4 w-4 mr-2" />
                  Share
                </Button>
              </div>
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="grid grid-cols-2 gap-3">
          <StatCard label="Total Referrals" value={referrals.length} />
          <StatCard label="Total Earned" value={totalEarned} prefix="ETB " />
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-white">How It Works</h3>
          </div>
          <div className="bg-habesha-surface/80 border border-white/10 rounded-3xl p-5 space-y-4">
            {[
              { step: 1, text: "Share your referral code with friends", icon: <Share2 className="h-5 w-5 text-habesha-gold" /> },
              { step: 2, text: "Friends sign up using your code", icon: <Users className="h-5 w-5 text-habesha-green" /> },
              { step: 3, text: "You both get ETB 50 bonus!", icon: <Gift className="h-5 w-5 text-habesha-gold" /> },
            ].map((item) => (
              <div key={item.step} className="flex items-center gap-3">
                <div className="h-8 w-8 rounded-xl bg-habesha-surface-light flex items-center justify-center shrink-0">
                  {item.icon}
                </div>
                <p className="text-sm text-white/80">{item.text}</p>
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="space-y-3">
          <h3 className="font-semibold text-white">Your Referrals</h3>
          {referralsQuery.isLoading ? (
            Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-14 rounded-2xl" />)
          ) : referrals.length === 0 ? (
            <EmptyState
              icon={<Users className="h-12 w-12" />}
              title="No referrals yet"
              description="Share your code to start earning rewards!"
              actionLabel="Share Now"
              onAction={handleShare}
            />
          ) : (
            <div className="space-y-2">
              {referrals.map((ref: any) => (
                <div key={ref.id} className="bg-habesha-surface/80 border border-white/10 rounded-2xl p-4 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Avatar src={ref.photo_url} fallback={ref.username?.[0]?.toUpperCase()} size="sm" />
                    <div>
                      <p className="text-sm font-medium text-white">{ref.username || `User ${ref.user_id?.slice(0, 6)}`}</p>
                      <p className="text-xs text-white/60">{new Date(ref.created_at).toLocaleDateString()}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-habesha-green">+ETB {ref.earned || 50}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </motion.div>

        <div className="h-6" />
      </div>
    </PageContainer>
  );
}
