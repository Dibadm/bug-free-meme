import { motion } from "framer-motion";
import { Gift, Check } from "lucide-react";
import { useClaimDailyReward } from "@/lib/queries";
import { useHaptics } from "@/hooks";

interface DailyRewardDay {
  day: number;
  reward: number;
  claimed: boolean;
  isToday: boolean;
}

interface DailyRewardProps {
  days: DailyRewardDay[];
  className?: string;
}

export function DailyReward({ days, className = "" }: DailyRewardProps) {
  const haptics = useHaptics();
  const claimMutation = useClaimDailyReward();
  const today = days.find((d) => d.isToday);
  const canClaim = today && !today.claimed;

  const handleClaim = () => {
    if (!canClaim) return;
    haptics.success();
    claimMutation.mutate();
  };

  return (
    <div className={`bg-habesha-surface/80 backdrop-blur-xl border border-white/10 rounded-3xl p-5 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Gift className="h-5 w-5 text-habesha-gold" />
          <h3 className="font-semibold text-white">Daily Rewards</h3>
        </div>
        <span className="text-xs text-white/60">Day {today?.day || 1}/7</span>
      </div>

      <div className="grid grid-cols-7 gap-2">
        {days.map((day) => (
          <div
            key={day.day}
            className={[
              "relative flex flex-col items-center justify-center aspect-square rounded-2xl border transition-all duration-200",
              day.claimed
                ? "bg-habesha-gold/10 border-habesha-gold/30"
                : day.isToday
                  ? "bg-habesha-gold/5 border-habesha-gold/50 shadow-lg shadow-habesha-gold/10"
                  : "bg-habesha-surface-light border-white/10",
            ]
              .filter(Boolean)
              .join(" ")}
          >
            <span className={`text-xs font-medium ${day.claimed ? "text-habesha-gold" : "text-white/60"}`}>
              {day.claimed ? <Check className="h-4 w-4" /> : `D${day.day}`}
            </span>
            <span className={`text-[10px] mt-0.5 ${day.claimed ? "text-habesha-gold/80" : "text-white/40"}`}>
              {day.reward} ETB
            </span>
            {day.isToday && !day.claimed && (
              <span className="absolute -top-1 -right-1 h-2 w-2 rounded-full bg-habesha-gold animate-pulse" />
            )}
          </div>
        ))}
      </div>

      {canClaim && (
        <motion.button
          whileTap={{ scale: 0.97 }}
          onClick={handleClaim}
          disabled={claimMutation.isPending}
          className="mt-4 w-full py-3.5 bg-habesha-gold text-habesha-dark font-bold rounded-2xl shadow-lg shadow-habesha-gold/20 active:scale-95 transition-all disabled:opacity-50"
        >
          {claimMutation.isPending ? "Claiming..." : `Claim Day ${today.day} Reward (${today.reward} ETB)`}
        </motion.button>
      )}

      {!canClaim && today?.claimed && (
        <div className="mt-4 text-center">
          <p className="text-sm text-white/60">Come back tomorrow for more rewards!</p>
        </div>
      )}
    </div>
  );
}
