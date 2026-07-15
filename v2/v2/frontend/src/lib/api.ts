import axios from "axios";

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
});

api.interceptors.request.use((config) => {
  const initData = localStorage.getItem("telegram_init_data");
  if (initData) {
    config.headers["X-Telegram-Init-Data"] = initData;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("telegram_init_data");
    }
    return Promise.reject(error);
  }
);

export async function validateTelegramUser(initData: string) {
  const response = await api.post("/auth/validate", { init_data: initData });
  return response.data;
}

export async function getRooms() {
  const response = await api.get("/rooms");
  return response.data;
}

export async function getGame(gameId: string) {
  const response = await api.get(`/games/${gameId}`);
  return response.data;
}

export async function getWalletBalance(userId: string) {
  const response = await api.get(`/wallet/balance?user_id=${userId}`);
  return response.data;
}

export async function getProfile() {
  const response = await api.get("/auth/me");
  return response.data;
}

export async function updateProfile(data: Record<string, unknown>) {
  const response = await api.patch("/profile", data);
  return response.data;
}

export async function getDeposits() {
  const response = await api.get("/wallet/deposits");
  return response.data;
}

export async function getWithdrawals() {
  const response = await api.get("/wallet/withdrawals");
  return response.data;
}

export async function createDeposit(amount: number, proofUrl: string) {
  const response = await api.post("/wallet/deposit", { amount, proof_url: proofUrl });
  return response.data;
}

export async function createDepositWithSms(amount: number, smsCode: string) {
  const response = await api.post("/wallet/deposit", { amount, sms_code: smsCode });
  return response.data;
}

export async function verifySms(depositId: string, smsText: string) {
  const response = await api.post(`/wallet/deposit/verify-sms`, { deposit_id: depositId, sms_text: smsText });
  return response.data;
}

export async function getPaymentSettings() {
  const response = await api.get("/payment-settings");
  return response.data;
}

export async function getAdminPaymentSettings() {
  const response = await api.get("/admin/payment-settings");
  return response.data;
}

export async function updateAdminPaymentSettings(data: Record<string, unknown>) {
  const response = await api.patch("/admin/payment-settings", data);
  return response.data;
}

export async function createWithdrawal(amount: number, phoneNumber: string) {
  const response = await api.post("/wallet/withdraw", { amount, phone_number: phoneNumber });
  return response.data;
}

export async function getTransactions() {
  const response = await api.get("/wallet/transactions");
  return response.data;
}

export async function getAnnouncements() {
  const response = await api.get("/announcements");
  return response.data;
}

export async function getLeaderboard(period: string = "weekly") {
  const response = await api.get(`/leaderboard?period=${period}`);
  return response.data;
}

export async function getReferrals() {
  const response = await api.get("/referrals");
  return response.data;
}

export async function getAchievements() {
  const response = await api.get("/achievements");
  return response.data;
}

export async function getDailyReward() {
  const response = await api.get("/daily-rewards");
  return response.data;
}

export async function claimDailyReward() {
  const response = await api.post("/daily-rewards/claim");
  return response.data;
}

export async function getStatistics() {
  const response = await api.get("/statistics");
  return response.data;
}

export async function searchUsers(query: string) {
  const response = await api.get(`/users/search?q=${encodeURIComponent(query)}`);
  return response.data;
}

export async function createGame(roomId: string) {
  const response = await api.post("/games", { room_id: roomId });
  return response.data;
}

export async function markNumber(gameId: string, number: number, cardIndices: number[]) {
  const response = await api.post(`/games/${gameId}/mark`, { number, card_indices: cardIndices });
  return response.data;
}

export async function claimPrize(gameId: string) {
  const response = await api.post(`/games/${gameId}/claim`);
  return response.data;
}

export async function transferBalance(toUserId: string, amount: number) {
  const response = await api.post("/wallet/transfer", { to_user_id: toUserId, amount });
  return response.data;
}
