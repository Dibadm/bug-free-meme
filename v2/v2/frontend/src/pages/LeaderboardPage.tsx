import { useState } from "react";
import { motion } from "framer-motion";
import { Crown, Medal, TrendingUp } from "lucide-react";
import { useLeaderboard } from "@/lib/queries";
import { useAuth as _useAuth } from "@/lib/useAuth";
import { useHaptics } from "@/hooks";
import { useToast } from "@/components/Toast";
import { TopNav, PageContainer, Tabs, Skeleton, Avatar } from "@/components";

type Period = "weekly" | "monthly" | "all_time";

export default function LeaderboardPage() {
  const [period, setPeriod] = useState<Period>("weekly");
  const { user } = _useAuth();
  const haptics = useHaptics();
  const toast = useToast();

  const leaderboardQuery = useLeaderboard(period);

  const handleShare = () => {
    haptics.medium();
    if (navigator.share) {
      navigator.share({ title: "Habesha Bet Leaderboard", text: "Check out the leaderboard!" });
    } else {
      toast("Leaderboard shared!", "success");
    }
  };

  const tabs = [
    { id: "weekly", label: "Weekly" },
    { id: "monthly", label: "Monthly" },
    { id: "all_time", label: "All Time" },
  ];

  const getRankIcon = (rank: number) => {
    if (rank === 1) return <Crown className="h-5 w-5 text-habesha-gold" />;
    if (rank === 2) return <Medal className="h-5 w-5 text-gray-300" />;
    if (rank === 3) return <Medal className="h-5 w-5 text-orange-400" />;
    return <span className="text-sm font-bold text-white/60">{rank}</span>;
  };

  return (
    <PageContainer>
      <TopNav title="Leaderboard" rightAction={<button onClick={handleShare} className="p-2 rounded-xl hover:bg-white/5 transition-colors"><TrendingUp className="h-5 w-5 text-white/60" /></button>} />

      <div className="p-4 space-y-5">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
          <Tabs tabs={tabs} activeTab={period} onChange={(id) => setPeriod(id as Period)} />

          {leaderboardQuery.isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-16 rounded-2xl" />
              ))}
            </div>
          ) : leaderboardQuery.data && leaderboardQuery.data.length > 0 ? (
            <div className="space-y-3">
              {leaderboardQuery.data.map((entry: any, idx: number) => {
                const isCurrentUser = user && entry.user_id === user.id;
                return (
                  <motion.div
                    key={entry.id || entry.user_id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    className={[
                      "bg-habesha-surface/80 backdrop-blur-xl border rounded-3xl p-4 flex items-center gap-4 transition-all",
                      isCurrentUser ? "border-habesha-gold/30 shadow-lg shadow-habesha-gold/5" : "border-white/10",
                    ]
                      .filter(Boolean)
                      .join(" ")}
                  >
                    <div className="flex items-center justify-center w-8 shrink-0">{getRankIcon(idx + 1)}</div>
                    <Avatar src={entry.photo_url} fallback={entry.username?.[0]?.toUpperCase()} size="md" />
                    <div className="flex-1 min-w-0">
                      <p className={`font-medium truncate ${isCurrentUser ? "text-habesha-gold" : "text-white"}`}>
                        {entry.username || `User ${entry.user_id?.slice(0, 6)}`}
                      </p>
                      <p className="text-xs text-white/60">{entry.games_played || 0} games</p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-habesha-gold">{entry.score?.toLocaleString() || 0}</p>
                      <p className="text-[10px] text-white/60 uppercase tracking-wider">points</p>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          ) : (
            <div className="bg-habesha-surface/80 border border-white/10 rounded-3xl p-8 text-center">
              <p className="text-white/60 text-sm">No rankings available for this period yet.</p>
            </div>
          )}
        </motion.div>

        <div className="h-6" />
      </div>
    </PageContainer>
  );
}
