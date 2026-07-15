import { useState, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Users, Trophy, Ticket } from "lucide-react";
import { useRoom, useWalletBalance } from "@/lib/queries";
import { useAuth } from "@/lib/useAuth";
import { useHaptics } from "@/hooks";
import { useToast } from "@/components/Toast";
import {
  TopNav,
  PageContainer,
  Button,
  Badge,
  Progress,
  Modal,
  Skeleton,
} from "@/components";

export default function RoomPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const haptics = useHaptics();
  const toast = useToast();
  const { user } = useAuth();
  const roomQuery = useRoom(id || "");
  const balanceQuery = useWalletBalance();

  const [selectedCards, setSelectedCards] = useState<number[]>([]);
  const [showPurchaseModal, setShowPurchaseModal] = useState(false);
  const [isPurchasing, setIsPurchasing] = useState(false);

  const room = roomQuery.data;
  const balance = balanceQuery.data?.balance || user?.balance || 0;

  const cards = useMemo(() => {
    if (!room) return [];
    const total = room.max_cards || 100;
    return Array.from({ length: total }, (_, i) => ({
      id: i + 1,
      numbers: generateBingoNumbers(),
      available: !room.cards_sold || i >= (room.cards_sold || 0),
    }));
  }, [room]);

  const entryFee = room?.entry_fee || room?.entryFee || 0;
  const totalCost = selectedCards.length * entryFee;
  const canAfford = balance >= totalCost;

  const toggleCard = (cardId: number) => {
    haptics.light();
    setSelectedCards((prev) =>
      prev.includes(cardId) ? prev.filter((c) => c !== cardId) : [...prev, cardId]
    );
  };

  const quickSelect = () => {
    haptics.medium();
    const available = cards.filter((c) => c.available && !selectedCards.includes(c.id));
    const toSelect = available.slice(0, 3 - selectedCards.length);
    setSelectedCards((prev) => [...new Set([...prev, ...toSelect.map((c) => c.id)])]);
  };

  const handlePurchase = async () => {
    if (!canAfford) {
      toast("Insufficient balance", "error");
      haptics.error();
      return;
    }
    setIsPurchasing(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 1500));
      toast("Cards purchased successfully!", "success");
      haptics.success();
      setShowPurchaseModal(false);
      setSelectedCards([]);
    } catch {
      toast("Purchase failed. Please try again.", "error");
    } finally {
      setIsPurchasing(false);
    }
  };

  if (roomQuery.isLoading) {
    return (
      <PageContainer withNav={false}>
        <div className="p-4 space-y-4">
          <Skeleton className="h-16 rounded-3xl" />
          <Skeleton className="h-32 rounded-3xl" />
          <Skeleton className="h-64 rounded-3xl" />
        </div>
      </PageContainer>
    );
  }

  if (!room) {
    return (
      <PageContainer withNav={false}>
        <div className="p-4 text-center text-white/60">Room not found</div>
      </PageContainer>
    );
  }

  return (
    <PageContainer withNav={false}>
      <TopNav
        title={room.name}
        onBack={() => navigate(-1)}
        rightAction={
          <Badge variant={room.is_live ? "success" : "default"}>
            {room.is_live ? "LIVE" : "UPCOMING"}
          </Badge>
        }
      />

      <div className="p-4 space-y-5">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
          <div className="bg-habesha-surface/80 backdrop-blur-xl border border-white/10 rounded-3xl p-5 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-white">{room.name}</h2>
                <p className="text-sm text-white/60 mt-1">
                  {room.pattern || "Classic Bingo"} pattern
                </p>
              </div>
              <div className="text-right">
                <p className="text-lg font-bold text-habesha-gold">ETB {entryFee}</p>
                <p className="text-xs text-white/60">Entry Fee</p>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div className="bg-habesha-surface-light/50 rounded-2xl p-3 text-center">
                <Trophy className="h-5 w-5 text-habesha-gold mx-auto mb-1" />
                <p className="text-xs text-white/60">Prize Pool</p>
                <p className="text-sm font-bold text-white">ETB {room.prize_pool?.toLocaleString()}</p>
              </div>
              <div className="bg-habesha-surface-light/50 rounded-2xl p-3 text-center">
                <Users className="h-5 w-5 text-habesha-green mx-auto mb-1" />
                <p className="text-xs text-white/60">Players</p>
                <p className="text-sm font-bold text-white">{room.players_count || 0}/{room.max_players}</p>
              </div>
              <div className="bg-habesha-surface-light/50 rounded-2xl p-3 text-center">
                <Ticket className="h-5 w-5 text-blue-400 mx-auto mb-1" />
                <p className="text-xs text-white/60">Cards</p>
                <p className="text-sm font-bold text-white">{room.cards_sold || 0}/{room.max_cards}</p>
              </div>
            </div>

            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="text-white/60">Cards sold</span>
                <span className="text-white/80 font-medium">{room.cards_sold || 0}/{room.max_cards}</span>
              </div>
              <Progress value={room.cards_sold || 0} max={room.max_cards || 100} />
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-white">Select Cards</h3>
            <button onClick={quickSelect} className="text-xs text-habesha-gold font-medium hover:underline">
              Quick Select
            </button>
          </div>
          <p className="text-xs text-white/60">Choose {selectedCards.length}/3 cards</p>
          <div className="grid grid-cols-3 gap-2">
            {cards.slice(0, 9).map((card) => (
              <motion.div
                key={card.id}
                whileTap={{ scale: 0.95 }}
                onClick={() => card.available && toggleCard(card.id)}
                className={[
                  "aspect-square rounded-2xl border p-2 flex flex-col items-center justify-center transition-all duration-200",
                  !card.available
                    ? "bg-habesha-surface/50 border-white/5 opacity-40"
                    : selectedCards.includes(card.id)
                      ? "bg-habesha-gold/10 border-habesha-gold/40 shadow-lg shadow-habesha-gold/10"
                      : "bg-habesha-surface-light border-white/10 hover:border-white/20",
                ]
                  .filter(Boolean)
                  .join(" ")}
              >
                <p className="text-[10px] text-white/60 mb-0.5">#{card.id}</p>
                <p className="text-xs font-bold text-white">ETB {entryFee}</p>
                {selectedCards.includes(card.id) && (
                  <span className="text-[10px] text-habesha-gold mt-0.5">SELECTED</span>
                )}
              </motion.div>
            ))}
          </div>
        </motion.div>

        {selectedCards.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="fixed bottom-24 left-0 right-0 z-30 p-4"
          >
            <div className="max-w-lg mx-auto">
              <Button
                onClick={() => setShowPurchaseModal(true)}
                disabled={!canAfford}
                className="shadow-2xl shadow-habesha-gold/20"
              >
                Purchase {selectedCards.length} Card{selectedCards.length > 1 ? "s" : ""} - ETB {totalCost}
              </Button>
            </div>
          </motion.div>
        )}

        <Modal isOpen={showPurchaseModal} onClose={() => setShowPurchaseModal(false)} title="Confirm Purchase">
          <div className="space-y-4">
            <div className="bg-habesha-surface-light/50 rounded-2xl p-4 space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-white/60">Cards</span>
                <span className="text-white font-medium">{selectedCards.length}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-white/60">Price per card</span>
                <span className="text-white font-medium">ETB {entryFee}</span>
              </div>
              <div className="border-t border-white/10 pt-2 flex items-center justify-between">
                <span className="text-white font-medium">Total</span>
                <span className="text-lg font-bold text-habesha-gold">ETB {totalCost}</span>
              </div>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-white/60">Your Balance</span>
              <span className="text-white font-medium">ETB {balance.toFixed(2)}</span>
            </div>
            <Button
              onClick={handlePurchase}
              loading={isPurchasing}
              disabled={!canAfford}
              className="w-full"
            >
              {canAfford ? `Pay ETB ${totalCost}` : "Insufficient Balance"}
            </Button>
          </div>
        </Modal>

        <div className="h-6" />
      </div>
    </PageContainer>
  );
}

function generateBingoNumbers() {
  const cols = [
    Array.from({ length: 15 }, (_, i) => i + 1),
    Array.from({ length: 15 }, (_, i) => i + 16),
    Array.from({ length: 15 }, (_, i) => i + 31),
    Array.from({ length: 15 }, (_, i) => i + 46),
    Array.from({ length: 15 }, (_, i) => i + 61),
  ];

  const numbers: number[] = [];
  for (let col = 0; col < 5; col++) {
    const colNums = cols[col].sort(() => Math.random() - 0.5).slice(0, 5);
    numbers.push(...colNums.sort((a, b) => a - b));
  }

  const shuffled: number[] = [];
  for (let i = 0; i < 5; i++) {
    for (let j = 0; j < 5; j++) {
      if (i === 2 && j === 2) {
        shuffled.push(0);
      } else {
        shuffled.push(numbers[i * 5 + j]);
      }
    }
  }
  return shuffled;
}
