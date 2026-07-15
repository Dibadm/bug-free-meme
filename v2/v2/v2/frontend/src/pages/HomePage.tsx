import { useMemo } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import {
  Gift,
  ChevronRight,
  RefreshCw,
} from "lucide-react";
import { useRooms, useAnnouncements, useStatistics, useDailyReward, useWalletBalance } from "@/lib/queries";
import { useAuth } from "@/lib/useAuth";
import { useHaptics } from "@/hooks";
import {
  BalanceCard,
  RoomCard,
  AnnouncementCarousel,
  DailyReward,
  StatCard,
  Skeleton,
} from "@/components";
import { PageContainer } from "@/components/PageContainer";

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.05 },
  },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
};

export default function HomePage() {
  const navigate = useNavigate();
  const haptics = useHaptics();
  const { user } = useAuth();
  const roomsQuery = useRooms();
  const announcementsQuery = useAnnouncements();
  const statsQuery = useStatistics();
  const dailyRewardQuery = useDailyReward();
  const balanceQuery = useWalletBalance();

  const liveRooms = useMemo(() => {
    if (!roomsQuery.data) return [];
    return roomsQuery.data.filter((r: any) => r.is_live || r.status === "live");
  }, [roomsQuery.data]);

  const upcomingRooms = useMemo(() => {
    if (!roomsQuery.data) return [];
    return roomsQuery.data.filter((r: any) => !r.is_live && r.status !== "live").slice(0, 5);
  }, [roomsQuery.data]);

  const dailyDays = useMemo(() => {
    const today = dailyRewardQuery.data?.today || 1;
    const claimed = dailyRewardQuery.data?.claimed_days || [];
    return Array.from({ length: 7 }, (_, i) => ({
      day: i + 1,
      reward: Math.floor(Math.random() * 50) + 10,
      claimed: claimed.includes(i + 1),
      isToday: i + 1 === today,
    }));
  }, [dailyRewardQuery.data]);

  const balance = balanceQuery.data?.balance || user?.balance || 0;
  const bonus = balanceQuery.data?.bonus || 0;

  const handleRefresh = () => {
    haptics.light();
    roomsQuery.refetch();
    announcementsQuery.refetch();
    statsQuery.refetch();
    balanceQuery.refetch();
  };

  return (
    <PageContainer>
      <motion.div variants={container} initial="hidden" animate="show" className="p-4 space-y-5">
        <motion.div variants={item} className="flex items-center justify-between pt-2">
          <div>
            <h1 className="text-2xl font-bold text-white">Habesha Bet</h1>
            <p className="text-sm text-white/60">Premium Bingo</p>
          </div>
          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={handleRefresh}
            className="p-2.5 rounded-2xl bg-habesha-surface/80 border border-white/10 text-white/70 hover:text-white transition-colors"
          >
            <RefreshCw className="h-5 w-5" />
          </motion.button>
        </motion.div>

        <motion.div variants={item}>
          <BalanceCard balance={balance} bonus={bonus} />
        </motion.div>

        <motion.div variants={item}>
          <AnnouncementCarousel announcements={announcementsQuery.data || []} />
        </motion.div>

        {liveRooms.length > 0 && (
          <motion.section variants={item} className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="relative flex h-2.5 w-2.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-habesha-green opacity-75" />
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-habesha-green" />
                </span>
                <h2 className="text-lg font-semibold text-white">Live Now</h2>
              </div>
            </div>
            <div className="space-y-3">
              {liveRooms.map((room: any) => (
                <RoomCard
                  key={room.id}
                  id={room.id}
                  name={room.name}
                  entryFee={room.entry_fee || room.entryFee}
                  prizePool={room.prize_pool || room.prizePool}
                  playersCount={room.players_count || room.playersCount}
                  maxPlayers={room.max_players || room.maxPlayers}
                  isLive
                  cardsSold={room.cards_sold || room.cardsSold}
                  maxCards={room.max_cards || room.maxCards}
                  onClick={() => navigate(`/room/${room.id}`)}
                />
              ))}
            </div>
          </motion.section>
        )}

        <motion.section variants={item} className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Upcoming Rooms</h2>
            <span className="text-xs text-white/60">{upcomingRooms.length} rooms</span>
          </div>
          <div className="space-y-3">
            {upcomingRooms.length === 0 ? (
              <div className="bg-habesha-surface/80 border border-white/10 rounded-3xl p-6 text-center">
                <p className="text-white/60 text-sm">No upcoming rooms. Check back later!</p>
              </div>
            ) : (
              upcomingRooms.map((room: any) => (
                <RoomCard
                  key={room.id}
                  id={room.id}
                  name={room.name}
                  entryFee={room.entry_fee || room.entryFee}
                  prizePool={room.prize_pool || room.prizePool}
                  playersCount={room.players_count || room.playersCount}
                  maxPlayers={room.max_players || room.maxPlayers}
                  startsAt={room.starts_at || room.startsAt}
                  cardsSold={room.cards_sold || room.cardsSold}
                  maxCards={room.max_cards || room.maxCards}
                  onClick={() => navigate(`/room/${room.id}`)}
                />
              ))
            )}
          </div>
        </motion.section>

        <motion.section variants={item} className="space-y-3">
          <h2 className="text-lg font-semibold text-white">Quick Stats</h2>
          <div className="grid grid-cols-2 gap-3">
            {statsQuery.isLoading ? (
              <>
                <Skeleton className="h-24 rounded-2xl" />
                <Skeleton className="h-24 rounded-2xl" />
                <Skeleton className="h-24 rounded-2xl" />
                <Skeleton className="h-24 rounded-2xl" />
              </>
            ) : statsQuery.data ? (
              <>
                <StatCard label="Games Played" value={statsQuery.data.games_played || 0} />
                <StatCard label="Win Rate" value={statsQuery.data.win_rate || 0} suffix="%" />
                <StatCard label="Cards Bought" value={statsQuery.data.cards_purchased || 0} />
                <StatCard label="Total Winnings" value={statsQuery.data.total_winnings || 0} prefix="ETB " />
              </>
            ) : (
              <div className="col-span-2 text-center text-white/60 text-sm py-4">
                No stats available yet. Start playing to see your stats!
              </div>
            )}
          </div>
        </motion.section>

        <motion.div variants={item}>
          <DailyReward days={dailyDays} />
        </motion.div>

        <motion.div variants={item} className="space-y-3">
          <h2 className="text-lg font-semibold text-white">Refer & Earn</h2>
          <motion.button
            whileTap={{ scale: 0.98 }}
            onClick={() => navigate("/referral")}
            className="w-full bg-habesha-surface/80 backdrop-blur-xl border border-white/10 rounded-3xl p-5 flex items-center justify-between active:bg-habesha-surface/90 transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-2xl bg-habesha-gold/10 flex items-center justify-center">
                <Gift className="h-5 w-5 text-habesha-gold" />
              </div>
              <div className="text-left">
                <p className="font-medium text-white text-sm">Invite Friends</p>
                <p className="text-xs text-white/60">Earn ETB 50 for each referral</p>
              </div>
            </div>
            <ChevronRight className="h-5 w-5 text-white/40" />
          </motion.button>
        </motion.div>

        <div className="h-6" />
      </motion.div>
    </PageContainer>
  );
}
