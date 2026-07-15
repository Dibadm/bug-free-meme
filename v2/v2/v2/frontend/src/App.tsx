import { Routes, Route, useLocation, Navigate, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { BottomNav } from "@/components/BottomNav";
import { useAuth } from "@/lib/useAuth";
import HomePage from "@/pages/HomePage";
import RoomPage from "@/pages/RoomPage";
import GamePage from "@/pages/GamePage";
import WinnerPage from "@/pages/WinnerPage";
import LoserPage from "@/pages/LoserPage";
import WalletPage from "@/pages/WalletPage";
import ProfilePage from "@/pages/ProfilePage";
import LeaderboardPage from "@/pages/LeaderboardPage";
import ReferralPage from "@/pages/ReferralPage";
import AdminPaymentSettingsPage from "@/pages/AdminPaymentSettingsPage";

const pages = [
  { id: "home", path: "/", label: "Home", icon: null },
  { id: "wallet", path: "/wallet", label: "Wallet", icon: null },
  { id: "profile", path: "/profile", label: "Profile", icon: null },
];

export default function App() {
  const location = useLocation();
  const navigate = useNavigate();
  const active = pages.find((p) => location.pathname === p.path) || pages[0];
  const { isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-habesha-dark flex items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-habesha-gold border-t-transparent" />
      </div>
    );
  }

  const showNav = !location.pathname.includes("/game") && !location.pathname.includes("/winner") && !location.pathname.includes("/loser");

  return (
    <div className="min-h-screen bg-habesha-dark">
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<PageTransition><HomePage /></PageTransition>} />
          <Route path="/room/:id" element={<RoomPage />} />
          <Route path="/game/:id" element={<GamePage />} />
          <Route path="/winner" element={<PageTransition><WinnerPage /></PageTransition>} />
          <Route path="/loser" element={<PageTransition><LoserPage /></PageTransition>} />
          <Route path="/wallet" element={<PageTransition><WalletPage /></PageTransition>} />
          <Route path="/profile" element={<PageTransition><ProfilePage /></PageTransition>} />
          <Route path="/leaderboard" element={<PageTransition><LeaderboardPage /></PageTransition>} />
          <Route path="/referral" element={<PageTransition><ReferralPage /></PageTransition>} />
          <Route path="/admin/payment-settings" element={<AdminPaymentSettingsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AnimatePresence>
      {showNav && (
        <BottomNav
          active={active.id}
          onNavigate={(path) => {
            const target = pages.find((p) => p.id === path);
            if (target) navigate(target.path);
          }}
        />
      )}
    </div>
  );
}

function PageTransition({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.2 }}
    >
      {children}
    </motion.div>
  );
}
