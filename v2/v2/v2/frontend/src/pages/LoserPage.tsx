import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { RotateCcw, Shield, Clock } from "lucide-react";
import { Countdown } from "@/components/Countdown";
import { PageContainer } from "@/components/PageContainer";
import { Button } from "@/components/Button";

export default function LoserPage() {
  const navigate = useNavigate();
  const winnerName = "@ab***12";
  const prize = 2500;
  const winningPattern = "Full House";

  const nextGameTime = useMemoNextGame();

  return (
    <PageContainer withNav={false}>
      <div className="min-h-screen flex flex-col items-center justify-center p-6 text-center">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.4 }}
          className="mb-6"
        >
          <div className="h-20 w-20 rounded-full bg-habesha-surface-light border border-white/10 flex items-center justify-center">
            <span className="text-4xl">🎯</span>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="space-y-3"
        >
          <h1 className="text-3xl font-bold text-white">Close One!</h1>
          <p className="text-white/60 text-sm max-w-xs">
            <span className="text-habesha-gold font-semibold">{winnerName}</span> got the Bingo with{" "}
            <span className="text-white font-medium">{winningPattern}</span> pattern and won ETB {prize}.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mt-6 w-full max-w-xs"
        >
          <div className="bg-habesha-surface/80 backdrop-blur-xl border border-white/10 rounded-3xl p-5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-white/60">Winner</span>
              <span className="text-sm font-medium text-habesha-gold">{winnerName}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-white/60">Winning Pattern</span>
              <span className="text-sm font-medium text-white">{winningPattern}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-white/60">Prize</span>
              <span className="text-sm font-bold text-habesha-green">ETB {prize}</span>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="mt-6 w-full max-w-xs space-y-3"
        >
          <div className="flex items-center justify-center gap-2 text-white/60">
            <Clock className="h-4 w-4" />
            <span className="text-sm">Next game in</span>
          </div>
          <Countdown end={nextGameTime} className="justify-center" />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="mt-8 w-full max-w-xs space-y-3"
        >
          <Button onClick={() => navigate("/")} size="lg" className="w-full">
            <RotateCcw className="h-5 w-5 mr-2" />
            Play Again
          </Button>
          <div className="flex items-center justify-center gap-2 text-white/40 text-xs">
            <Shield className="h-3 w-3" />
            Provably fair - verify anytime
          </div>
        </motion.div>
      </div>
    </PageContainer>
  );
}

function useMemoNextGame() {
  const now = new Date();
  const next = new Date(now);
  next.setHours(next.getHours() + 1);
  next.setMinutes(0, 0, 0);
  return next;
}
