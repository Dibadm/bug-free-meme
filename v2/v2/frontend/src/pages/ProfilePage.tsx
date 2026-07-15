import { motion } from "framer-motion";
import { useState } from "react";
import { Settings, LogOut, Copy, Share2, Flame, Award, Target } from "lucide-react";
import { useProfile, useAchievements } from "@/lib/queries";
import { useAuth } from "@/lib/useAuth";
import { useHaptics } from "@/hooks";
import { useToast } from "@/components/Toast";
import {
  TopNav,
  PageContainer,
  Button,
  Badge,
  Avatar,
  StatCard,
  Progress,
  Sheet,
  Skeleton,
} from "@/components";

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const profileQuery = useProfile();
  const achievementsQuery = useAchievements();
  const haptics = useHaptics();
  const toast = useToast();

  const [showSettings, setShowSettings] = useState(false);

  const profile = profileQuery.data || user;
  const achievements = achievementsQuery.data || [];

  const handleCopyCode = () => {
    haptics.light();
    if (profile?.referral_code) {
      navigator.clipboard.writeText(profile.referral_code);
      toast("Referral code copied!", "success");
    }
  };

  const handleShare = () => {
    haptics.medium();
    if (navigator.share && profile?.referral_code) {
      navigator.share({
        title: "Join Habesha Bet",
        text: `Use my referral code ${profile.referral_code} to join!`,
      });
    }
  };

  const handleLogout = () => {
    haptics.medium();
    logout();
    toast("Logged out successfully", "info");
  };

  if (profileQuery.isLoading) {
    return (
      <PageContainer>
        <div className="p-4 space-y-4">
          <Skeleton className="h-20 rounded-3xl" />
          <Skeleton className="h-32 rounded-3xl" />
          <Skeleton className="h-48 rounded-3xl" />
        </div>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <TopNav title="Profile" rightAction={<button onClick={() => setShowSettings(true)} className="p-2 rounded-xl hover:bg-white/5 transition-colors"><Settings className="h-5 w-5 text-white/60" /></button>} />

      <div className="p-4 space-y-5">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex items-center gap-4">
          <Avatar src={profile?.photo_url} fallback={profile?.username || profile?.first_name} size="lg" className="h-16 w-16 text-xl border-2 border-habesha-gold/30" />
          <div className="flex-1 min-w-0">
            <h2 className="text-xl font-bold text-white truncate">{profile?.username || "Player"}</h2>
            <div className="flex items-center gap-2 mt-1">
              <Badge variant="gold">{profile?.role || "player"}</Badge>
              {profile?.streak_days ? (
                <span className="flex items-center gap-1 text-xs text-orange-400">
                  <Flame className="h-3 w-3" />
                  {profile.streak_days} day streak
                </span>
              ) : null}
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="grid grid-cols-2 gap-3">
          <StatCard label="Games Played" value={profile?.games_played || 0} />
          <StatCard label="Games Won" value={profile?.games_won || 0} />
          <StatCard label="Win Rate" value={profile?.win_rate || 0} suffix="%" />
          <StatCard label="Cards Bought" value={profile?.cards_purchased || 0} />
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="space-y-3">
          <h3 className="font-semibold text-white flex items-center gap-2">
            <Award className="h-5 w-5 text-habesha-gold" />
            Achievements
          </h3>
          {achievements.length === 0 ? (
            <div className="bg-habesha-surface/80 border border-white/10 rounded-3xl p-4 text-center">
              <p className="text-sm text-white/60">No achievements yet. Keep playing!</p>
            </div>
          ) : (
            <div className="space-y-2">
              {achievements.slice(0, 5).map((achievement: any) => (
                <div key={achievement.id} className="bg-habesha-surface/80 border border-white/10 rounded-2xl p-4 flex items-center gap-3">
                  <div className="h-10 w-10 rounded-2xl bg-habesha-gold/10 flex items-center justify-center shrink-0">
                    <Target className="h-5 w-5 text-habesha-gold" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-white">{achievement.name}</p>
                    <p className="text-xs text-white/60">{achievement.description}</p>
                    <Progress value={achievement.progress || 0} max={achievement.target || 100} size="sm" />
                  </div>
                </div>
              ))}
            </div>
          )}
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="space-y-3">
          <h3 className="font-semibold text-white">Referral Program</h3>
          <div className="bg-habesha-surface/80 backdrop-blur-xl border border-white/10 rounded-3xl p-5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-white/60">Your Code</span>
              <div className="flex items-center gap-2">
                <span className="text-sm font-mono font-bold text-habesha-gold">{profile?.referral_code || "N/A"}</span>
                <button onClick={handleCopyCode} className="p-1.5 rounded-lg hover:bg-white/5 transition-colors">
                  <Copy className="h-4 w-4 text-white/60" />
                </button>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-white/60">Total Referrals</span>
              <span className="text-sm font-bold text-white">{profile?.total_referrals || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-white/60">Total Earned</span>
              <span className="text-sm font-bold text-habesha-green">ETB {profile?.total_earned || 0}</span>
            </div>
            <Button variant="secondary" onClick={handleShare} className="w-full">
              <Share2 className="h-4 w-4 mr-2" />
              Share Referral Code
            </Button>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <Button variant="danger" onClick={handleLogout} className="w-full">
            <LogOut className="h-4 w-4 mr-2" />
            Logout
          </Button>
        </motion.div>

        <div className="h-6" />
      </div>

      <Sheet isOpen={showSettings} onClose={() => setShowSettings(false)} title="Settings">
        <div className="space-y-3">
          <div className="bg-habesha-surface-light/50 rounded-2xl p-4 flex items-center justify-between">
            <span className="text-white font-medium">Language</span>
            <span className="text-white/60 text-sm">English</span>
          </div>
          <div className="bg-habesha-surface-light/50 rounded-2xl p-4 flex items-center justify-between">
            <span className="text-white font-medium">Notifications</span>
            <Badge variant="success">Enabled</Badge>
          </div>
          <div className="bg-habesha-surface-light/50 rounded-2xl p-4 flex items-center justify-between cursor-pointer hover:bg-habesha-surface-light transition-colors">
            <span className="text-white font-medium">Support</span>
            <span className="text-white/60 text-sm">Contact us</span>
          </div>
        </div>
      </Sheet>
    </PageContainer>
  );
}
