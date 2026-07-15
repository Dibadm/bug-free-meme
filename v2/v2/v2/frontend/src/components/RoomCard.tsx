import { motion } from "framer-motion";
import { Countdown } from "./Countdown";
import { Badge } from "./Badge";
import { Users, Trophy, Timer } from "lucide-react";

interface RoomCardProps {
  id: string;
  name: string;
  entryFee: number;
  prizePool: number;
  playersCount: number;
  maxPlayers: number;
  isLive?: boolean;
  startsAt?: string | Date;
  cardsSold?: number;
  maxCards?: number;
  onClick?: () => void;
  className?: string;
}

export function RoomCard({
  name,
  entryFee,
  prizePool,
  playersCount,
  maxPlayers,
  isLive = false,
  startsAt,
  cardsSold = 0,
  maxCards = 100,
  onClick,
  className = "",
}: RoomCardProps) {
  const fillPercent = Math.min((cardsSold / maxCards) * 100, 100);

  return (
    <motion.div
      whileHover={{ y: -2 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={[
        "relative overflow-hidden bg-habesha-surface/80 backdrop-blur-xl border border-white/10 rounded-3xl p-5 cursor-pointer transition-shadow hover:shadow-lg hover:shadow-habesha-gold/5",
        className,
      ]
        .filter(Boolean)
        .join(" ")}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />
      <div className="relative z-10 space-y-3">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="font-semibold text-white text-lg">{name}</h3>
            <div className="flex items-center gap-2 mt-1">
              {isLive && (
                <span className="flex items-center gap-1.5">
                  <span className="relative flex h-2.5 w-2.5">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-habesha-green opacity-75" />
                    <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-habesha-green" />
                  </span>
                  <span className="text-xs font-medium text-habesha-green">LIVE</span>
                </span>
              )}
              {!isLive && startsAt && (
                <span className="flex items-center gap-1 text-xs text-white/60">
                  <Timer className="h-3 w-3" />
                  <Countdown end={new Date(startsAt)} />
                </span>
              )}
            </div>
          </div>
          <Badge variant="gold">ETB {entryFee}</Badge>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5 text-white/60">
            <Trophy className="h-4 w-4 text-habesha-gold" />
            <span className="text-sm font-medium text-habesha-gold">ETB {prizePool.toLocaleString()}</span>
          </div>
          <div className="flex items-center gap-1.5 text-white/60">
            <Users className="h-4 w-4" />
            <span className="text-sm">{playersCount}/{maxPlayers}</span>
          </div>
        </div>

        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-xs">
            <span className="text-white/60">Cards sold</span>
            <span className="text-white/80 font-medium">{cardsSold}/{maxCards}</span>
          </div>
          <div className="h-2 bg-habesha-surface-light rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-habesha-gold to-habesha-gold-dark rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${fillPercent}%` }}
              transition={{ duration: 0.8, ease: "easeOut" }}
            />
          </div>
        </div>

        <motion.button
          whileTap={{ scale: 0.97 }}
          className={[
            "w-full py-3.5 rounded-2xl font-bold text-sm transition-all duration-200",
            isLive
              ? "bg-habesha-green text-habesha-dark shadow-lg shadow-habesha-green/20"
              : "bg-habesha-gold text-habesha-dark shadow-lg shadow-habesha-gold/20",
          ]
            .filter(Boolean)
            .join(" ")}
          onClick={(e) => {
            e.stopPropagation();
            onClick?.();
          }}
        >
          {isLive ? "Join Game" : "Join Room"}
        </motion.button>
      </div>
    </motion.div>
  );
}
