import { useState, useEffect, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Wifi, WifiOff, Trophy, Volume2, VolumeX } from "lucide-react";
import { useGame } from "@/lib/queries";
import { useHaptics } from "@/hooks";
import { useToast } from "@/components/Toast";
import { TopNav,
  PageContainer,
  Button,
  Badge,
  BingoCard,
  LiveBall,
  Confetti,
  Skeleton,
} from "@/components";

export default function GamePage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const haptics = useHaptics();
  const toast = useToast();

  const gameQuery = useGame(id || "");
  const [isConnected] = useState(true);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [showConfetti, setShowConfetti] = useState(false);
  const [manualMode, setManualMode] = useState(false);

  const game = gameQuery.data;

  const calledNumbers = useMemo(() => game?.called_numbers || [], [game?.called_numbers]);
  const currentNumber = useMemo(() => calledNumbers[calledNumbers.length - 1], [calledNumbers]);
  const playerCards = useMemo(() => game?.player_cards || [], [game?.player_cards]);
  const markedNumbers = useMemo(() => game?.player_marked || [], [game?.player_marked]);

  useEffect(() => {
    if (currentNumber) {
      haptics.light();
      if (soundEnabled) {
        try {
          const audio = new Audio("/sounds/ball.mp3");
          audio.volume = 0.3;
          audio.play().catch(() => {});
        } catch {
          // ignore audio errors
        }
      }
    }
  }, [currentNumber, haptics, soundEnabled]);

  const handleBingo = async () => {
    haptics.success();
    setShowConfetti(true);
    toast("BINGO! Checking your card...", "success");
    setTimeout(() => {
      toast("Congratulations! You won!", "success");
      setTimeout(() => navigate("/winner"), 2000);
    }, 1500);
  };

  if (gameQuery.isLoading) {
    return (
      <PageContainer withNav={false}>
        <div className="p-4 space-y-4">
          <Skeleton className="h-16 rounded-3xl" />
          <Skeleton className="h-64 rounded-3xl" />
        </div>
      </PageContainer>
    );
  }

  if (!game) {
    return (
      <PageContainer withNav={false}>
        <div className="p-4 text-center text-white/60">Game not found</div>
      </PageContainer>
    );
  }

  return (
    <PageContainer withNav={false}>
      <TopNav
        title={game.room_name || "Game"}
        onBack={() => navigate(-1)}
        rightAction={
          <div className="flex items-center gap-2">
            <button
              onClick={() => setSoundEnabled(!soundEnabled)}
              className="p-2 rounded-xl hover:bg-white/5 transition-colors"
            >
              {soundEnabled ? <Volume2 className="h-5 w-5 text-white/60" /> : <VolumeX className="h-5 w-5 text-white/60" />}
            </button>
            <Badge variant={isConnected ? "success" : "danger"}>
              {isConnected ? <Wifi className="h-3 w-3" /> : <WifiOff className="h-3 w-3" />}
              {isConnected ? "LIVE" : "OFFLINE"}
            </Badge>
          </div>
        }
      />

      <div className="p-4 space-y-5">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-white/60">Status</p>
              <Badge variant={game.status === "live" ? "success" : "warning"}>
                {game.status?.toUpperCase() || "WAITING"}
              </Badge>
            </div>
            <div className="text-right">
              <p className="text-sm text-white/60">Prize Pool</p>
              <p className="text-xl font-bold text-habesha-gold">ETB {game.prize_pool?.toLocaleString()}</p>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-2">
            <div className="bg-habesha-surface-light/50 rounded-2xl p-3 text-center">
              <p className="text-[10px] text-white/60 uppercase tracking-wider">Called</p>
              <p className="text-lg font-bold text-white">{calledNumbers.length}/75</p>
            </div>
            <div className="bg-habesha-surface-light/50 rounded-2xl p-3 text-center">
              <p className="text-[10px] text-white/60 uppercase tracking-wider">Players</p>
              <p className="text-lg font-bold text-white">{game.players_count || 0}</p>
            </div>
            <div className="bg-habesha-surface-light/50 rounded-2xl p-3 text-center">
              <p className="text-[10px] text-white/60 uppercase tracking-wider">Pattern</p>
              <p className="text-sm font-bold text-white mt-1">{game.pattern || "Classic"}</p>
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="flex flex-col items-center py-6">
          <p className="text-xs text-white/60 uppercase tracking-widest mb-3">Current Number</p>
          <AnimatePresence mode="wait">
            {currentNumber ? (
              <motion.div
                key={currentNumber}
                initial={{ scale: 0, rotate: -180, opacity: 0 }}
                animate={{ scale: 1, rotate: 0, opacity: 1 }}
                exit={{ scale: 0, rotate: 180, opacity: 0 }}
                transition={{ type: "spring", stiffness: 260, damping: 20 }}
              >
                <LiveBall number={currentNumber} size="lg" isNew />
              </motion.div>
            ) : (
              <div className="h-20 w-20 rounded-full bg-habesha-surface-light border border-white/10 flex items-center justify-center">
                <span className="text-white/30 text-sm">Waiting...</span>
              </div>
            )}
          </AnimatePresence>
        </motion.div>

        {calledNumbers.length > 0 && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-2">
            <p className="text-xs text-white/60 uppercase tracking-wider">Called Numbers</p>
            <div className="flex gap-1.5 overflow-x-auto pb-2 hide-scrollbar">
              {calledNumbers.slice(-15).map((num: number, idx: number) => (
                <motion.div
                  key={`${num}-${idx}`}
                  initial={{ opacity: 0, scale: 0 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ type: "spring", stiffness: 500, damping: 25 }}
                >
                  <span className="inline-flex items-center justify-center h-8 w-8 rounded-lg bg-habesha-surface-light border border-white/10 text-xs font-medium text-white/80">
                    {num}
                  </span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-white">Your Cards</h3>
            <button
              onClick={() => setManualMode(!manualMode)}
              className="text-xs text-white/60 hover:text-white transition-colors"
            >
              {manualMode ? "Auto Mark" : "Manual Mode"}
            </button>
          </div>
          {playerCards.length === 0 ? (
            <div className="bg-habesha-surface/80 border border-white/10 rounded-3xl p-6 text-center">
              <p className="text-white/60 text-sm">No cards selected for this game</p>
            </div>
          ) : (
            <div className="space-y-3">
              {playerCards.map((card: any, idx: number) => (
                <div key={card.id || idx} className="space-y-1">
                  <p className="text-xs text-white/60">Card {idx + 1}</p>
                  <BingoCard
                    numbers={card.numbers || card}
                    calledNumbers={calledNumbers}
                    markedNumbers={card.marked || markedNumbers}
                    winningPattern={game.winning_pattern}
                    size="sm"
                  />
                </div>
              ))}
            </div>
          )}
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Button onClick={handleBingo} size="lg" className="w-full shadow-2xl shadow-habesha-green/20">
            <Trophy className="h-5 w-5 mr-2" />
            BINGO!
          </Button>
        </motion.div>

        <div className="h-6" />
      </div>

      <Confetti trigger={showConfetti} onComplete={() => setShowConfetti(false)} />
    </PageContainer>
  );
}
