import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "./api";
import { useToast } from "@/components/Toast";

export function useRooms() {
  return useQuery({
    queryKey: ["rooms"],
    queryFn: () => api.get("/rooms").then((r) => r.data),
  });
}

export function useRoom(id: string) {
  return useQuery({
    queryKey: ["rooms", id],
    queryFn: () => api.get(`/rooms/${id}`).then((r) => r.data),
    enabled: !!id,
  });
}

export function useGame(id: string) {
  return useQuery({
    queryKey: ["games", id],
    queryFn: () => api.get(`/games/${id}`).then((r) => r.data),
    enabled: !!id,
    refetchInterval: 2000,
  });
}

export function useWalletBalance() {
  return useQuery({
    queryKey: ["wallet", "balance"],
    queryFn: () => api.get("/wallet/balance").then((r) => r.data),
    refetchInterval: 10000,
  });
}

export function useDeposits() {
  return useQuery({
    queryKey: ["wallet", "deposits"],
    queryFn: () => api.get("/wallet/deposits").then((r) => r.data),
  });
}

export function useWithdrawals() {
  return useQuery({
    queryKey: ["wallet", "withdrawals"],
    queryFn: () => api.get("/wallet/withdrawals").then((r) => r.data),
  });
}

export function useTransactions() {
  return useQuery({
    queryKey: ["wallet", "transactions"],
    queryFn: () => api.get("/wallet/transactions").then((r) => r.data),
  });
}

export function useAnnouncements() {
  return useQuery({
    queryKey: ["announcements"],
    queryFn: () => api.get("/announcements").then((r) => r.data),
    staleTime: 1000 * 60,
  });
}

export function useLeaderboard(period: string = "weekly") {
  return useQuery({
    queryKey: ["leaderboard", period],
    queryFn: () => api.get(`/leaderboard?period=${period}`).then((r) => r.data),
    staleTime: 1000 * 60,
  });
}

export function useReferrals() {
  return useQuery({
    queryKey: ["referrals"],
    queryFn: () => api.get("/referrals").then((r) => r.data),
  });
}

export function useAchievements() {
  return useQuery({
    queryKey: ["achievements"],
    queryFn: () => api.get("/achievements").then((r) => r.data),
  });
}

export function useStatistics() {
  return useQuery({
    queryKey: ["statistics"],
    queryFn: () => api.get("/statistics").then((r) => r.data),
    staleTime: 1000 * 60,
  });
}

export function useDailyReward() {
  return useQuery({
    queryKey: ["dailyReward"],
    queryFn: () => api.get("/daily-rewards").then((r) => r.data),
  });
}

export function useProfile() {
  return useQuery({
    queryKey: ["profile"],
    queryFn: () => api.get("/auth/me").then((r) => r.data),
  });
}

export function useCreateDeposit() {
  const queryClient = useQueryClient();
  const toast = useToast();
  return useMutation({
    mutationFn: ({ amount, proofUrl, smsCode }: { amount: number; proofUrl?: string; smsCode?: string }) =>
      api.post("/wallet/deposit", { amount, proof_url: proofUrl, sms_code: smsCode }).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["wallet", "balance"] });
      queryClient.invalidateQueries({ queryKey: ["wallet", "transactions"] });
      queryClient.invalidateQueries({ queryKey: ["wallet", "deposits"] });
      toast("Deposit submitted successfully", "success");
    },
    onError: () => {
      toast("Failed to create deposit", "error");
    },
  });
}

export function useCreateWithdrawal() {
  const queryClient = useQueryClient();
  const toast = useToast();
  return useMutation({
    mutationFn: ({ amount, phoneNumber }: { amount: number; phoneNumber: string }) =>
      api.post("/wallet/withdraw", { amount, phone_number: phoneNumber }).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["wallet", "balance"] });
      queryClient.invalidateQueries({ queryKey: ["wallet", "transactions"] });
      queryClient.invalidateQueries({ queryKey: ["wallet", "withdrawals"] });
      toast("Withdrawal request submitted", "success");
    },
    onError: () => {
      toast("Failed to create withdrawal", "error");
    },
  });
}

export function useClaimDailyReward() {
  const queryClient = useQueryClient();
  const toast = useToast();
  return useMutation({
    mutationFn: () => api.post("/daily-rewards/claim").then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dailyReward"] });
      queryClient.invalidateQueries({ queryKey: ["wallet", "balance"] });
      queryClient.invalidateQueries({ queryKey: ["profile"] });
      toast("Daily reward claimed!", "success");
    },
    onError: () => {
      toast("Failed to claim daily reward", "error");
    },
  });
}

export function useSearchUsers() {
  return useQuery({
    queryKey: ["users", "search"],
    queryFn: ({ queryKey }: { queryKey: [string, string] }) =>
      api.get(`/users/search?q=${encodeURIComponent(queryKey[1])}`).then((r) => r.data),
    enabled: false,
  });
}
