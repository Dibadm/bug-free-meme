import { useState } from "react";
import { motion } from "framer-motion";
import { Trophy, Share2, RotateCcw, Crown } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Confetti } from "@/components/Confetti";
import { PageContainer } from "@/components/PageContainer";
import { Button } from "@/components/Button";

export default function WinnerPage() {
  const navigate = useNavigate();
  const [showConfetti, setShowConfetti] = useState(true);

  const prize = 2500;
  const winnerName = "@ab***12";

  return (
    <PageContainer withNav={false}>
      <Confetti trigger={showConfetti} onComplete={() => setShowConfetti(false)} />

      <div className="min-h-screen flex flex-col items-center justify-center p-6 text-center">
        <motion.div
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ type: "spring", stiffness: 260, damping: 20 }}
          className="mb-6"
        >
          <div className="h-24 w-24 rounded-full bg-gradient-to-br from-habesha-gold to-habesha-gold-dark flex items-center justify-center shadow-2xl shadow-habesha-gold/40">
            <Crown className="h-12 w-12 text-habesha-dark" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="space-y-3"
        >
          <h1 className="text-4xl font-bold text-white">BINGO!</h1>
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-habesha-gold/10 border border-habesha-gold/30 rounded-full">
            <Trophy className="h-5 w-5 text-habesha-gold" />
            <span className="text-sm font-medium text-habesha-gold">Winner</span>
          </div>
          <p className="text-white/60 text-sm">
            Congratulations <span className="text-habesha-gold font-semibold">{winnerName}</span>!
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mt-8 w-full max-w-xs"
        >
          <div className="bg-habesha-surface/80 backdrop-blur-xl border border-white/10 rounded-3xl p-6 space-y-4">
            <div className="text-center">
              <p className="text-xs text-white/60 uppercase tracking-wider mb-1">Prize Won</p>
              <p className="text-4xl font-bold text-habesha-gold">ETB {prize.toLocaleString()}</p>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-habesha-surface-light/50 rounded-2xl p-3 text-center">
                <p className="text-xs text-white/60">Pattern</p>
                <p className="text-sm font-bold text-white mt-1">Full House</p>
              </div>
              <div className="bg-habesha-surface-light/50 rounded-2xl p-3 text-center">
                <p className="text-xs text-white/60">Cards</p>
                <p className="text-sm font-bold text-white mt-1">3</p>
              </div>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="mt-8 w-full max-w-xs space-y-3"
        >
          <Button onClick={() => navigate("/")} size="lg" className="w-full">
            <RotateCcw className="h-5 w-5 mr-2" />
            Play Again
          </Button>
          <Button
            variant="secondary"
            onClick={() => {
              if (navigator.share) {
                navigator.share({ title: "I Won Bingo!", text: `I just won ETB ${prize} on Habesha Bet!` });
              }
            }}
            className="w-full"
          >
            <Share2 className="h-5 w-5 mr-2" />
            Share Victory
          </Button>
        </motion.div>
      </div>
    </PageContainer>
  );
}
